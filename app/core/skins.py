import os
import urllib.request
import urllib.error
import json
import time
import shutil
from typing import Optional, Dict, Tuple


class SkinSystem:
    SKIN_URL = "http://skinsystem.ely.by/skins/{username}.png"
    CAPE_URL = "http://skinsystem.ely.by/cloaks/{username}.png"
    TEXTURES_URL = "http://skinsystem.ely.by/textures/{username}"
    LEGACY_SKIN_URL = "http://s3.amazonaws.com/MinecraftSkins/{username}.png"
    CACHE_TTL = 3600

    def __init__(self, game_dir: str, cache_dir: Optional[str] = None):
        self.game_dir = game_dir
        self.cache_dir = cache_dir or os.path.join(game_dir, ".skin_cache")
        self.skins_dir = os.path.join(game_dir, "skins")
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.skins_dir, exist_ok=True)
        self.cache_meta_file = os.path.join(self.cache_dir, "cache_meta.json")
        self.cache_meta = self._load_cache_meta()
        
    def _load_cache_meta(self) -> Dict:
        if os.path.exists(self.cache_meta_file):
            try:
                with open(self.cache_meta_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_cache_meta(self):
        try:
            with open(self.cache_meta_file, 'w') as f:
                json.dump(self.cache_meta, f)
        except Exception:
            pass
    
    def _is_cache_valid(self, username: str) -> bool:
        username_lower = username.lower()
        if username_lower not in self.cache_meta:
            return False
        return (time.time() - self.cache_meta[username_lower].get("timestamp", 0)) < self.CACHE_TTL
    
    def _download_file(self, url: str, dest_path: str) -> bool:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'MeoLauncher/1.0'})
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(response.read())
                    return True
        except Exception:
            pass
        return False
    
    def download_skin(self, username: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        username_lower = username.lower()
        cache_path = os.path.join(self.cache_dir, f"{username_lower}.png")
        
        if not force and self._is_cache_valid(username) and os.path.exists(cache_path):
            return True, cache_path
        
        for url in [self.SKIN_URL.format(username=username), self.LEGACY_SKIN_URL.format(username=username)]:
            if self._download_file(url, cache_path):
                self.cache_meta[username_lower] = {"timestamp": time.time(), "url": url}
                self._save_cache_meta()
                return True, cache_path
        
        return False, None
    
    def download_cape(self, username: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        username_lower = username.lower()
        cache_path = os.path.join(self.cache_dir, f"{username_lower}_cape.png")
        cache_key = f"{username_lower}_cape"
        
        if not force and cache_key in self.cache_meta:
            if (time.time() - self.cache_meta[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
                if os.path.exists(cache_path):
                    return True, cache_path
        
        if self._download_file(self.CAPE_URL.format(username=username), cache_path):
            self.cache_meta[cache_key] = {"timestamp": time.time()}
            self._save_cache_meta()
            return True, cache_path
        
        return False, None
    
    def apply_skin_to_game(self, username: str, skin_path: Optional[str] = None) -> bool:
        dest_path = os.path.join(self.skins_dir, f"{username}.png")
        
        if skin_path and os.path.exists(skin_path):
            try:
                shutil.copy2(skin_path, dest_path)
                return True
            except Exception:
                return False
        
        success, downloaded_path = self.download_skin(username)
        if success and downloaded_path:
            try:
                shutil.copy2(downloaded_path, dest_path)
                return True
            except Exception:
                pass
        return False
    
    def apply_cape_to_game(self, username: str) -> bool:
        capes_dir = os.path.join(self.game_dir, "cloaks")
        os.makedirs(capes_dir, exist_ok=True)
        dest_path = os.path.join(capes_dir, f"{username}.png")
        
        success, downloaded_path = self.download_cape(username)
        if success and downloaded_path:
            try:
                shutil.copy2(downloaded_path, dest_path)
                return True
            except Exception:
                pass
        return False
    
    def get_textures_info(self, username: str) -> Optional[Dict]:
        try:
            request = urllib.request.Request(
                self.TEXTURES_URL.format(username=username),
                headers={'User-Agent': 'MeoLauncher/1.0'}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
        except Exception:
            pass
        return None
    
    def setup_for_launch(self, username: str, custom_skin_path: Optional[str] = None, on_log=None) -> Dict[str, bool]:
        results = {"skin": False, "cape": False}
        
        if custom_skin_path and os.path.exists(custom_skin_path):
            results["skin"] = self.apply_skin_to_game(username, custom_skin_path)
        else:
            results["skin"] = self.apply_skin_to_game(username)
            
        results["cape"] = self.apply_cape_to_game(username)
        return results
    
    def clear_cache(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_meta = {}
        self._save_cache_meta()
    
    def get_elyby_profile(self, username: str) -> Optional[Dict]:
        try:
            request = urllib.request.Request(
                f"http://skinsystem.ely.by/profile/{username}",
                headers={'User-Agent': 'MeoLauncher/1.0'}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return {"id": data.get("id", ""), "name": data.get("name", username), "source": "elyby"}
        except Exception:
            pass
        return None


def get_elyby_uuid(username: str) -> Optional[str]:
    try:
        request = urllib.request.Request(
            f"http://skinsystem.ely.by/profile/{username}",
            headers={'User-Agent': 'MeoLauncher/1.0'}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8')).get("id")
    except Exception:
        pass
    return None


def download_skin_from_elyby(username: str, dest_path: str) -> bool:
    try:
        request = urllib.request.Request(
            f"http://skinsystem.ely.by/skins/{username}.png",
            headers={'User-Agent': 'MeoLauncher/1.0'}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'wb') as f:
                    f.write(response.read())
                return True
    except Exception:
        pass
    return False
