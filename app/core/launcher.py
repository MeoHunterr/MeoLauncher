import os
import platform
import sys


class DependencyResolver:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else root_dir
            self.game_dir = os.path.join(base, "app", "game")
        else:
            self.game_dir = os.path.join(root_dir, "app", "game")
             
        self.files_dir = self.game_dir
        self.libraries_dir = os.path.join(self.files_dir, "libraries")
        
    def resolve_classpath(self):
        classpath = []
        
        bta_jar = os.path.join(self.files_dir, "jarmods", "bta.jar")
        if os.path.exists(bta_jar):
            classpath.append(bta_jar)
            
        if os.path.exists(self.libraries_dir):
            for root, _, files in os.walk(self.libraries_dir):
                for file in files:
                    if "minecraft-b1.7.3-client.jar" in file:
                        classpath.append(os.path.join(root, file))
                        break
            
            for root, _, files in os.walk(self.libraries_dir):
                for file in files:
                    if not file.endswith(".jar"): continue
                    if any(x in file for x in ["fabric-loader", "intermediary", "minecraft-", "natives"]): continue
                    classpath.append(os.path.join(root, file))
        
        return os.pathsep.join(classpath)

    def get_natives(self):
        natives = []
        if not os.path.exists(self.libraries_dir):
            return natives
        
        system = platform.system().lower()
        native_suffix = {"windows": "natives-windows", "darwin": "natives-osx", "linux": "natives-linux"}.get(system)
        
        if native_suffix:
            for root, _, files in os.walk(self.libraries_dir):
                for file in files:
                    if native_suffix in file and file.endswith(".jar"):
                        natives.append(os.path.join(root, file))
        
        return natives
