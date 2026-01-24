import os
import platform
import zipfile
import sys
import logging

logger = logging.getLogger(__name__)


class AdvancedJavaManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else root_dir
            self.java_pkg_dir = os.path.join(base, "app", "java_pkg")
        else:
            self.java_pkg_dir = os.path.join(root_dir, "app", "java_pkg")
        self.java_target_dir = os.path.join(self.java_pkg_dir, "runtime")

    def get_java_executable(self):
        java_name = "java.exe" if platform.system().lower() == "windows" else "java"
        
        java_exe = os.path.join(self.java_target_dir, "bin", java_name)
        if os.path.exists(java_exe):
            return java_exe
        
        if os.path.exists(self.java_target_dir):
            for root, _, files in os.walk(self.java_target_dir):
                if java_name in files:
                    return os.path.join(root, java_name)
        
        self._extract_java()
        
        if os.path.exists(self.java_target_dir):
            for root, _, files in os.walk(self.java_target_dir):
                if java_name in files:
                    return os.path.join(root, java_name)
                    
        raise FileNotFoundError(f"Java not found in {self.java_pkg_dir}")

    def _extract_java(self):
        if not os.path.exists(self.java_pkg_dir):
            raise FileNotFoundError(f"Java package not found: {self.java_pkg_dir}")
        
        system = platform.system().lower()
        os_patterns = {"windows": ["win"], "darwin": ["mac", "osx"], "linux": ["linux"]}
        patterns = os_patterns.get(system, [])
        
        zip_path = None
        for f in os.listdir(self.java_pkg_dir):
            if f.endswith(".zip"):
                if any(p in f.lower() for p in patterns):
                    zip_path = os.path.join(self.java_pkg_dir, f)
                    break
        
        if not zip_path:
            for f in os.listdir(self.java_pkg_dir):
                if f.endswith(".zip"):
                    zip_path = os.path.join(self.java_pkg_dir, f)
                    break
                    
        if not zip_path:
            raise FileNotFoundError(f"No Java zip in {self.java_pkg_dir}")
            
        os.makedirs(self.java_target_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                member_path = os.path.normpath(os.path.join(self.java_target_dir, member))
                if not member_path.startswith(os.path.normpath(self.java_target_dir) + os.sep):
                    if member_path != os.path.normpath(self.java_target_dir):
                        raise ValueError(f"Path traversal: {member}")
                zf.extract(member, self.java_target_dir)

    def get_jvm_args(self, ram_mb=2048):
        return [
            f"-Xmx{ram_mb}M", "-XX:+UseG1GC", "-Dsun.rmi.dgc.server.gcInterval=2147483646",
            "-XX:+UnlockExperimentalVMOptions", "-XX:G1NewSizePercent=20", "-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=32M"
        ]

    def check_java_status(self):
        try:
            return f"Ready ({os.path.basename(self.get_java_executable())})"
        except (FileNotFoundError, OSError) as e:
            logger.debug("Java status check failed: %s", e)
            return "Missing"
