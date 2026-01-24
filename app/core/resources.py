import os
import sys
import shutil
import json
import hashlib
import tarfile
import time


class ResourceManager:
    ASSET_VERSION = "1.0.0"
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                self.assets_dir = os.path.join(sys._MEIPASS, "assets")
                self.app_dir = os.path.join(sys._MEIPASS, "app")
            else:
                self.assets_dir = os.path.join(root_dir, "assets")
                self.app_dir = os.path.join(root_dir, "app")
        else:
            self.assets_dir = os.path.join(root_dir, "assets")
            self.app_dir = os.path.join(root_dir, "app")
    
    def _get_manifest_path(self, target_app_dir):
        return os.path.join(target_app_dir, ".asset_manifest.json")
    
    def _load_manifest(self, target_app_dir):
        manifest_path = self._get_manifest_path(target_app_dir)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                pass
        return {}
    
    def _save_manifest(self, target_app_dir, manifest):
        manifest_path = self._get_manifest_path(target_app_dir)
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
    
    def _calculate_file_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        try:
            file_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    file_hash.update(chunk)
            return file_hash.hexdigest()
        except (IOError, OSError):
            return None
    
    def _validate_extraction(self, dest_dir, expected_files=None):
        if not os.path.exists(dest_dir) or not os.listdir(dest_dir):
            return False
        if expected_files:
            return all(os.path.exists(os.path.join(dest_dir, f)) for f in expected_files)
        return True

    def _needs_extraction(self, manifest, key, archive_path, dest_dir):
        cached = manifest.get(key, {})
        current_hash = self._calculate_file_hash(archive_path)
        
        if cached.get("version") != self.ASSET_VERSION:
            return True
        if current_hash != cached.get("archive_hash"):
            return True
        if not self._validate_extraction(dest_dir):
            return True
        return False

    def _extract_archive(self, archive_path, dest_dir, parent_dir, manifest, key):
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(parent_dir, exist_ok=True)
        
        def safe_members(tar_obj, dest_path):
            for member in tar_obj.getmembers():
                member_path = os.path.join(dest_path, member.name)
                if not os.path.abspath(member_path).startswith(os.path.abspath(dest_path)):
                    raise Exception(f"Path traversal: {member.name}")
                yield member
        
        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(parent_dir, members=safe_members(tar, parent_dir))
        
        manifest[key] = {
            "version": self.ASSET_VERSION,
            "archive_hash": self._calculate_file_hash(archive_path),
            "extracted_at": time.time()
        }

    def extract_assets(self, force=False):
        if getattr(sys, 'frozen', False):
            target_app_dir = os.path.join(os.path.dirname(sys.executable), "app")
        else:
            target_app_dir = self.app_dir
        
        manifest = self._load_manifest(target_app_dir)
        manifest_updated = False
        
        java_xz = os.path.join(self.assets_dir, "java_win.tar.xz")
        game_xz = os.path.join(self.assets_dir, "game.tar.xz")
        java_dest = os.path.join(target_app_dir, "java_pkg", "runtime")
        game_dest = os.path.join(target_app_dir, "game")
        
        if os.path.exists(java_xz) and (force or self._needs_extraction(manifest, "java", java_xz, java_dest)):
            self._extract_archive(java_xz, java_dest, os.path.join(target_app_dir, "java_pkg"), manifest, "java")
            manifest_updated = True
        
        if os.path.exists(game_xz) and (force or self._needs_extraction(manifest, "game", game_xz, game_dest)):
            self._extract_archive(game_xz, game_dest, target_app_dir, manifest, "game")
            manifest_updated = True
        
        if manifest_updated:
            self._save_manifest(target_app_dir, manifest)
        
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.join(os.path.dirname(sys.executable), "app")
    
    def clear_extracted_assets(self):
        if getattr(sys, 'frozen', False):
            target_app_dir = os.path.join(os.path.dirname(sys.executable), "app")
        else:
            target_app_dir = self.app_dir
        
        paths = [
            os.path.join(target_app_dir, "java_pkg"),
            os.path.join(target_app_dir, "game"),
            self._get_manifest_path(target_app_dir)
        ]
        
        deleted = False
        for path in paths:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    deleted = True
                except (IOError, OSError, PermissionError):
                    pass
        
        return deleted
