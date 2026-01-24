from app.core.anticheat import AntiCheat, SecurityViolation
from app.core.launcher import DependencyResolver
from app.core.integrity import InstanceDoctor
from app.core.java import AdvancedJavaManager
from app.core.skins import SkinSystem
import os
import sys
import subprocess
import threading
import logging

logger = logging.getLogger(__name__)


class LauncherService:
    ALLOWED_JVM_PREFIXES = ('-Xmx', '-Xms', '-Xmn', '-Xss', '-XX:', '-D')
    BLOCKED_JVM_PATTERNS = ('-agentpath', '-javaagent', '-agentlib', 'file:', 'http:', 'https:', '|', '&', ';', '`', '$')

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.resolver = DependencyResolver(root_dir)
        self.doctor = InstanceDoctor(root_dir)
        self.java_mgr = AdvancedJavaManager(root_dir)
        self.process = None
        self.anticheat = None
        self.skin_system = SkinSystem(self.resolver.game_dir)

    def launch(self, config, on_log=None, on_exit=None):
        def _run():
            try:
                game_dir = self.resolver.game_dir
                self.anticheat = AntiCheat(game_dir)
                
                try:
                    self.anticheat.scan_assets()
                    self.anticheat.scan_mods()
                except SecurityViolation as e:
                    if on_log: on_log(f"SECURITY: {e}")
                    if on_exit: on_exit(1)
                    return

                java_exe = config.get("java_path")
                if not java_exe or not os.path.exists(java_exe):
                    java_exe = self.java_mgr.get_java_executable()
                
                classpath = self.resolver.resolve_classpath()
                natives = self.resolver.get_natives()
                self.doctor.heal(natives)
                
                jvm_args = self.java_mgr.get_jvm_args(config.get("max_ram", 2048))
                perf = config.get("performance", {})
                
                if perf.get("microstutter", False):
                    jvm_args.extend(["-XX:+UseConcMarkSweepGC", "-XX:+CMSIncrementalMode", "-XX:-UseAdaptiveSizePolicy", "-Xmn128M"])
                    perf["g1gc"] = False
                
                if perf.get("g1gc", True):
                    jvm_args.extend(["-XX:+UseG1GC", "-XX:+UnlockExperimentalVMOptions", "-XX:G1NewSizePercent=20", 
                                     "-XX:G1ReservePercent=20", "-XX:MaxGCPauseMillis=50", "-XX:G1HeapRegionSize=32M"])
                
                if perf.get("pretouch", True): jvm_args.append("-XX:+AlwaysPreTouch")
                if perf.get("parallel", True): jvm_args.append("-XX:+ParallelRefProcEnabled")
                if perf.get("nobiasedlock", True): jvm_args.append("-XX:-UseBiasedLocking")
                if perf.get("codecache", True): jvm_args.extend(["-XX:ReservedCodeCacheSize=512m", "-XX:+UseCodeCacheFlushing"])
                if perf.get("inlining", True): jvm_args.extend(["-XX:MaxInlineSize=420", "-XX:FreqInlineSize=500", "-XX:InlineSmallCode=2000"])
                if perf.get("noexplicitgc", True): jvm_args.append("-XX:+DisableExplicitGC")
                if perf.get("tiered", True): jvm_args.extend(["-XX:+TieredCompilation", "-XX:TieredStopAtLevel=4"])
                if perf.get("stringdedup", False): jvm_args.append("-XX:+UseStringDeduplication")
                
                custom_args = config.get("custom_jvm_args", "")
                for arg in custom_args.split():
                    if any(b in arg.lower() for b in self.BLOCKED_JVM_PATTERNS): continue
                    if not any(arg.startswith(p) for p in self.ALLOWED_JVM_PREFIXES): continue
                    jvm_args.append(arg)

                username = config.get("username", "Player")
                uuid = config.get("uuid", "00000000-0000-0000-0000-000000000000")
                token = config.get("access_token", "0")
                
                try:
                    elyby_profile = self.skin_system.get_elyby_profile(username)
                    if elyby_profile and elyby_profile.get("id"):
                        uuid = elyby_profile["id"]
                except (IOError, OSError, ValueError) as e:
                    logger.debug("Ely.by profile lookup failed: %s", e)
                
                game_args = ["net.minecraft.client.Minecraft", "--username", username, "--session", token,
                             "--gameDir", game_dir, "--width", str(config.get("width", 854)),
                             "--height", str(config.get("height", 480)), "--uuid", uuid]
                
                try:
                    self.skin_system.setup_for_launch(username, config.get("skin_path"))
                except (IOError, OSError) as e:
                    logger.debug("Skin setup failed: %s", e)
                
                self._set_fullscreen_option(game_dir, config.get("fullscreen", False))
                
                authlib_path = self._find_authlib_injector()
                authlib_args = [f"-javaagent:{authlib_path}=https://authserver.ely.by"] if authlib_path else []
                
                full_cmd = [java_exe] + authlib_args + jvm_args + [f"-Djava.library.path={self.doctor.natives_dir}", "-cp", classpath] + game_args
                
                creation_flags = 0x00000010 if config.get("show_console", False) else 0x08000000
                
                self.process = subprocess.Popen(full_cmd, cwd=game_dir, stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=creation_flags)
                
                self.anticheat.monitor(self.process, lambda msg: on_log(f"SECURITY: {msg}") if on_log else None)
                
                while self.process.poll() is None:
                    line = self.process.stdout.readline()
                    if line and on_log: on_log(line.strip())
                        
                if on_exit: on_exit(self.process.returncode)
                    
            except Exception as e:
                logger.error("Launch failed: %s", e)
                if on_log: on_log(f"Error: {e}")
                if on_exit: on_exit(-1)

        threading.Thread(target=_run, daemon=True).start()

    def _find_authlib_injector(self):
        paths = [
            os.path.join(self.root_dir, "app", "authlib-injector.jar"),
            os.path.join(self.root_dir, "authlib-injector.jar"),
        ]
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                paths.extend([os.path.join(sys._MEIPASS, "app", "authlib-injector.jar"),
                              os.path.join(sys._MEIPASS, "authlib-injector.jar")])
            paths.extend([os.path.join(self.root_dir, "lib", "app", "authlib-injector.jar"),
                          os.path.join(os.path.dirname(sys.executable), "app", "authlib-injector.jar")])
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def _set_fullscreen_option(self, game_dir, enable):
        options_path = os.path.join(game_dir, "options.txt")
        if not os.path.exists(options_path): return
        
        try:
            with open(options_path, "r") as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if line.startswith("fullscreen:"):
                    new_lines.append(f"fullscreen:{str(enable).lower()}\n")
                elif line.startswith("startInFullscreen:"):
                    new_lines.append(f"startInFullscreen:{str(enable).lower()}\n")
                else:
                    new_lines.append(line)
            
            with open(options_path, "w") as f:
                f.writelines(new_lines)
        except (IOError, OSError) as e:
            logger.debug("Could not set fullscreen option: %s", e)
