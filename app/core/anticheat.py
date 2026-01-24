import os
import time
import threading
import zipfile
import io
import json

try:
    from PIL import Image
except ImportError:
    Image = None

class SecurityViolation(Exception):
    pass

class AntiCheat:
    BANNED_KEYWORDS = ["xray", "x-ray", "ore", "透视"]
    BANNED_MOD_IDS = ["wurst", "meteor-client", "aristois", "bleachhack", "liquidbounce", "baritone"]
    MONITORED_FOLDERS = ["texturepacks", "resourcepacks", "mods"]
    
    OPAQUE_BLOCK_COORDS = [
        (0, 1), (0, 2), (2, 2), (2, 1), (2, 0), (3, 2)
    ]

    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.stop_monitoring = False
        self.cache_file = os.path.join(game_dir, "anticheat_cache.json")
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f)
        except (IOError, OSError):
            pass

    def _get_file_hash(self, path):
        try:
            stat = os.stat(path)
            return f"{stat.st_size}-{stat.st_mtime}"
        except (IOError, OSError):
            return None

    def scan_assets(self):
        for folder in ["texturepacks", "resourcepacks"]:
            path = os.path.join(self.game_dir, folder)
            if not os.path.exists(path):
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    self._check_file(os.path.join(root, file))

    def scan_mods(self):
        mods_dir = os.path.join(self.game_dir, "mods")
        if not os.path.exists(mods_dir):
            return
        for root, _, files in os.walk(mods_dir):
            for file in files:
                if file.endswith((".jar", ".zip")):
                    self._check_mod_internal(os.path.join(root, file))

    def _check_mod_internal(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                if "fabric.mod.json" in zf.namelist():
                    with zf.open("fabric.mod.json") as f:
                        mod_id = json.load(f).get("id", "").lower()
                        if any(banned in mod_id for banned in self.BANNED_MOD_IDS):
                            raise SecurityViolation(f"Banned mod: {mod_id}")
                elif "mcmod.info" in zf.namelist():
                    with zf.open("mcmod.info") as f:
                        content = f.read().decode('utf-8', errors='ignore').lower()
                        if any(banned in content for banned in self.BANNED_MOD_IDS):
                            raise SecurityViolation(f"Banned mod in {os.path.basename(file_path)}")
        except zipfile.BadZipFile:
            pass
        except SecurityViolation:
            raise
        except (IOError, OSError, json.JSONDecodeError):
            pass

    def _check_file(self, file_path):
        file_hash = self._get_file_hash(file_path)
        if file_hash and file_path in self.cache and self.cache[file_path] == file_hash:
            return

        filename = os.path.basename(file_path).lower()
        
        if any(kw in filename for kw in self.BANNED_KEYWORDS):
            raise SecurityViolation(f"Banned resource: {filename}")
        
        if filename.endswith(".zip"):
            try:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for name in zf.namelist():
                        if any(kw in name.lower() for kw in self.BANNED_KEYWORDS):
                            raise SecurityViolation(f"Banned content: {name}")
                        if name.endswith("terrain.png") and Image:
                            with zf.open(name) as img_file:
                                self._analyze_terrain_png(img_file.read(), filename)
            except zipfile.BadZipFile:
                pass
            except SecurityViolation:
                raise
            except (IOError, OSError):
                pass
        
        if file_hash:
            self.cache[file_path] = file_hash
            self._save_cache()

    def _analyze_terrain_png(self, img_data, filename):
        try:
            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
            width, height = img.size
            tile_size = width // 16
            
            for row, col in self.OPAQUE_BLOCK_COORDS:
                origin_x, origin_y = col * tile_size, row * tile_size
                
                points = [
                    (origin_x + tile_size//2, origin_y + tile_size//2),
                    (origin_x + 2, origin_y + 2),
                    (origin_x + tile_size - 3, origin_y + 2),
                    (origin_x + 2, origin_y + tile_size - 3),
                    (origin_x + tile_size - 3, origin_y + tile_size - 3)
                ]
                
                transparent_count = sum(
                    1 for px, py in points 
                    if px < width and py < height and img.getpixel((px, py))[3] < 20
                )
                
                if transparent_count == 5:
                    raise SecurityViolation(f"X-ray detected: {filename}")
        except SecurityViolation:
            raise
        except (IOError, OSError, ValueError):
            pass

    def monitor(self, process, on_violation):
        def _watch():
            snapshots = {}
            for folder in self.MONITORED_FOLDERS:
                path = os.path.join(self.game_dir, folder)
                snapshots[folder] = set(os.listdir(path)) if os.path.exists(path) else set()
            
            while process.poll() is None and not self.stop_monitoring:
                for folder in self.MONITORED_FOLDERS:
                    path = os.path.join(self.game_dir, folder)
                    current_files = set()
                    
                    if os.path.exists(path):
                        with os.scandir(path) as entries:
                            current_files = {e.name for e in entries}
                    
                    added = current_files - snapshots[folder]
                    
                    for file in added:
                        file_path = os.path.join(path, file)
                        try:
                            if folder == "mods" and file.endswith((".jar", ".zip")):
                                self._check_mod_internal(file_path)
                            else:
                                self._check_file(file_path)
                        except SecurityViolation as e:
                            process.kill()
                            if on_violation:
                                on_violation(str(e))
                            return
                        except (IOError, OSError):
                            pass
                    
                    snapshots[folder] = current_files
                
                time.sleep(5)

        threading.Thread(target=_watch, daemon=True).start()
