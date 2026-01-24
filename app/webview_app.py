import webview
import sys
import os
import threading
import time
import ctypes
import urllib.request
import subprocess
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.service import LauncherService
from app.core.settings import SettingsManager
from app.core.resources import ResourceManager
from app.core.auth import MicrosoftAuth

try:
    from app.template_renderer import TemplateRenderer
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


def is_webview2_installed():
    import winreg
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
    ]
    for hkey, path in registry_paths:
        try:
            with winreg.OpenKey(hkey, path):
                return True
        except Exception:
            pass
    return False


def download_and_install_webview2():
    installer_url = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
    installer_path = Path(os.getcwd()) / "MicrosoftEdgeWebview2Setup.exe"
    
    ctypes.windll.user32.MessageBoxW(0, 
        "Microsoft Edge WebView2 Runtime is missing.\nClick OK to download and install.", 
        "Missing Component", 0x40 | 0x1)

    try:
        urllib.request.urlretrieve(installer_url, installer_path)
        
        if not installer_path.exists() or installer_path.stat().st_size < 100000:
            raise RuntimeError("Download failed or file corrupted")
        
        subprocess.run([str(installer_path), "/silent", "/install"], check=False, capture_output=True)
        
        if installer_path.exists():
            os.remove(installer_path)
            
        ctypes.windll.user32.MessageBoxW(0, "WebView2 installed successfully!", "Success", 0x40)
        return True
    except Exception as e:
        if installer_path.exists():
            os.remove(installer_path)
        ctypes.windll.user32.MessageBoxW(0, f"Failed: {e}\nInstall manually from:\nhttps://developer.microsoft.com/microsoft-edge/webview2/", "Error", 0x10)
        return False


class JSApi:
    def __init__(self, launcher_service, settings_mgr):
        self._window = None
        self.launcher = launcher_service
        self.settings = settings_mgr
        self.auth = None

    def set_window(self, window):
        self._window = window

    def launch_game(self):
        config = self.settings.settings
        
        if not config.get("uuid") or config.get("auth_type") == "offline":
            import uuid
            import hashlib
            username = config.get("username", "Player")
            hash_bytes = bytearray(hashlib.md5(f"OfflinePlayer:{username}".encode(), usedforsecurity=False).digest())
            hash_bytes[6] = (hash_bytes[6] & 0x0f) | 0x30
            hash_bytes[8] = (hash_bytes[8] & 0x3f) | 0x80
            config["uuid"] = str(uuid.UUID(bytes=bytes(hash_bytes)))

        def on_log(msg):
            if self._window:
                safe_msg = msg.replace("'", "\\'").replace('"', '\\"')
                self._window.evaluate_js(f"console.log('Game: {safe_msg}')")

        def on_exit(code):
            if self._window:
                self._window.evaluate_js("resetLaunchButton()")

        self.launcher.launch(config, on_log=on_log, on_exit=on_exit)
        return {"status": "success"}

    def get_settings(self):
        return self.settings.settings

    def save_settings(self, new_settings):
        for key, value in new_settings.items():
            self.settings.set(key, value)
        return {"status": "success"}
        
    def get_versions(self):
        return ["BTA v7.3_04", "1.7.3 (Beta)"]
    
    def get_system_info(self):
        try:
            import psutil
            total_ram_mb = psutil.virtual_memory().total // (1024 * 1024)
            recommended = min(max(total_ram_mb // 2, 2048), 8192)
            recommended = (recommended // 512) * 512
            return {"total_ram_mb": total_ram_mb, "recommended_ram_mb": recommended}
        except ImportError:
            return {"total_ram_mb": 8192, "recommended_ram_mb": 4096}

    def open_folder(self, folder_type):
        base_dir = self.launcher.root_dir
        folder_map = {
            "screenshots": os.path.join(base_dir, "screenshots"),
            "texturepacks": os.path.join(base_dir, "texturepacks"),
            "game": base_dir
        }
        path = folder_map.get(folder_type)
        if path:
            os.makedirs(path, exist_ok=True)
            os.startfile(path)
            return {"status": "success"}
        return {"status": "error", "message": "Unknown folder type"}
    
    def pick_background_image(self):
        try:
            import shutil
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=('Image Files (*.png;*.jpg;*.jpeg;*.webp)', 'All files (*.*)')
            )
            
            if result and len(result) > 0:
                src_path = result[0]
                dest_folder = self.settings.data_dir
                os.makedirs(dest_folder, exist_ok=True)
                ext = os.path.splitext(src_path)[1]
                dest_path = os.path.join(dest_folder, f"background{ext}")
                shutil.copy2(src_path, dest_path)
                self.settings.set("custom_background", dest_path)
                return {"status": "success", "path": dest_path}
            return {"status": "cancelled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def pick_skin_file(self):
        try:
            import shutil
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=('PNG Files (*.png)', 'All files (*.*)')
            )
            
            if result and len(result) > 0:
                src_path = result[0]
                dest_folder = os.path.join(self.settings.data_dir, "skins")
                os.makedirs(dest_folder, exist_ok=True)
                filename = os.path.basename(src_path)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy2(src_path, dest_path)
                self.settings.set("skin_path", dest_path)
                return {"status": "success", "path": dest_path, "filename": filename}
            return {"status": "cancelled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_custom_background(self):
        self.settings.set("custom_background", None)
        return {"status": "success"}

    def start_microsoft_login(self):
        try:
            from app.core.oauth_auth import MicrosoftAuthOAuth
            self.oauth = MicrosoftAuthOAuth()
            
            def on_success(account_info):
                profile = {
                    "name": account_info.get("name", "Player"),
                    "id": account_info.get("id", ""),
                    "access_token": account_info.get("access_token", ""),
                    "refresh_token": account_info.get("refresh_token", "")
                }
                self.settings.set("username", profile["name"])
                self.settings.set("uuid", profile["id"])
                self.settings.set("access_token", profile["access_token"])
                self.settings.set("refresh_token", profile.get("refresh_token", ""))
                self.settings.set("auth_type", "microsoft")
                
                if self._window:
                    self._window.evaluate_js(f"onLoginSuccess({json.dumps(profile)})")
            
            def on_error(error_msg):
                if self._window:
                    self._window.evaluate_js(f"onLoginError('{str(error_msg).replace(chr(39), chr(92)+chr(39))}')")
            
            result = self.oauth.start_login(on_success=on_success, on_error=on_error)
            
            if self._window:
                self._window.evaluate_js("updateLoginStatus('Opening browser...')")
            
            return result
            
        except ImportError as e:
            return {"status": "error", "message": f"Missing: {e}. Run: pip install minecraft-launcher-lib"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_elyby_login(self, username, password, totp_token=None):
        try:
            from app.core.elyby_auth import ElybyAuth, ElybyAuthError, ElybyTwoFactorRequired
            elyby = ElybyAuth(self.settings.data_dir)
            
            try:
                result = elyby.authenticate(username, password, totp_token)
                self.settings.set("username", result["username"])
                self.settings.set("uuid", result["uuid"])
                self.settings.set("access_token", result["access_token"])
                self.settings.set("auth_type", "elyby")
                
                if self._window:
                    self._window.evaluate_js(f"onLoginSuccess({json.dumps(result)})")
                
                return {"status": "success", "profile": result}
                
            except ElybyTwoFactorRequired:
                return {"status": "2fa_required", "message": "Enter 2FA code"}
            except ElybyAuthError as e:
                return {"status": "error", "message": str(e)}
                
        except ImportError as e:
            return {"status": "error", "message": f"Missing module: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def minimize(self):
        if self._window:
            self._window.minimize()

    def close(self):
        if self._window:
            self._window.destroy()
    
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
        return {"status": "success"}
    
    def clear_game_data(self):
        try:
            if getattr(sys, 'frozen', False):
                root_dir = os.path.dirname(sys.executable)
            else:
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            success = ResourceManager(root_dir).clear_extracted_assets()
            
            if success:
                return {"status": "success", "message": "Game data cleared. Re-extraction on next launch."}
            return {"status": "info", "message": "No data to clear."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    if not is_webview2_installed():
        if not download_and_install_webview2():
            sys.exit(1)

    if getattr(sys, 'frozen', False):
        root_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    settings_mgr = SettingsManager(root_dir)
    launcher_service = LauncherService(root_dir)
    api = JSApi(launcher_service, settings_mgr)

    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        possible_paths = [
            os.path.join(exe_dir, 'lib', 'app', 'assets', 'index.html'),
            os.path.join(exe_dir, 'app', 'assets', 'index.html'),
            os.path.join(exe_dir, 'assets', 'index.html'),
        ]
        main_html = next((p for p in possible_paths if os.path.exists(p)), possible_paths[0])
        loading_html = os.path.join(os.path.dirname(main_html), 'loading.html')
        if not os.path.exists(loading_html):
            loading_html = main_html
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        main_html = os.path.join(base_dir, 'assets', 'index.html')
        loading_html = os.path.join(base_dir, 'assets', 'loading.html')
        
        if JINJA2_AVAILABLE:
            templates_dir = os.path.join(base_dir, 'assets', 'templates')
            if os.path.exists(templates_dir):
                try:
                    TemplateRenderer(templates_dir).render_to_file(main_html, "base.html")
                except Exception:
                    pass

    window = webview.create_window(
        'Minecraft Launcher', 
        url=f'file:///{loading_html}',
        js_api=api,
        width=1280,
        height=720,
        frameless=True,
        easy_drag=True,
        min_size=(800, 600),
        background_color='#1f2022'
    )
    api.set_window(window)

    def init_sequence():
        time.sleep(0.5)
        try:
            window.evaluate_js("if(window.updateStatus) updateStatus('Extracting assets...');")
            ResourceManager(root_dir).extract_assets()
            window.evaluate_js("if(window.updateStatus) updateStatus('Ready!');")
            time.sleep(0.5)
            window.load_url(f'file:///{main_html}')
        except Exception as e:
            window.evaluate_js(f"alert('Error: {e}');")

    threading.Thread(target=init_sequence, daemon=True).start()
    webview.start(debug=settings_mgr.get("debug_mode"))


if __name__ == '__main__':
    main()
