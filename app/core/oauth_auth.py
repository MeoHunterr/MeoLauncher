import os
import sys
import threading
import webbrowser
import http.server
import urllib.parse
from dotenv import load_dotenv
from app.core.credentials import get_client_id

try:
    import minecraft_launcher_lib
    MINECRAFT_LIB_AVAILABLE = True
except ImportError:
    MINECRAFT_LIB_AVAILABLE = False

load_dotenv()

CLIENT_ID = None
REDIRECT_URL = "http://localhost:8080/callback"

def _get_client_id():
    global CLIENT_ID
    if CLIENT_ID is None:
        CLIENT_ID = get_client_id()
    return CLIENT_ID


class AuthCallback:
    def __init__(self):
        self.event = threading.Event()
        self.auth_code = None
        self.state = None
        self.error = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        
        if self.path.startswith('/callback'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            self.server.auth_callback.auth_code = params.get('code', [None])[0]
            self.server.auth_callback.state = params.get('state', [None])[0]
            self.server.auth_callback.error = params.get('error', [None])[0]
            self.server.auth_callback.event.set()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            status = "❌ Login Failed" if self.server.auth_callback.error else "✓ Login Successful"
            color = "#ff4444" if self.server.auth_callback.error else "#39d353"
            html = f'''<html><head><style>body{{font-family:'Segoe UI',sans-serif;background:#1a1b1d;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center}}</style></head><body><h1 style="color:{color}">{status}</h1><p style="color:#999">You can close this window.</p></body></html>'''
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


class MicrosoftAuthOAuth:
    def __init__(self):
        if not MINECRAFT_LIB_AVAILABLE:
            raise ImportError("minecraft_launcher_lib required")
        self.client_id = _get_client_id()
        self.redirect_url = REDIRECT_URL
        self.server = None
    
    def start_login(self, on_success=None, on_error=None):
        login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(
            self.client_id, self.redirect_url
        )
        login_url += "&prompt=select_account"
        
        auth_callback = AuthCallback()
        self.server = http.server.HTTPServer(('localhost', 8080), CallbackHandler)
        self.server.auth_callback = auth_callback
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        webbrowser.open(login_url)
        
        def wait_for_callback():
            try:
                if auth_callback.event.wait(timeout=300):
                    if auth_callback.error:
                        if on_error: on_error(f"Login error: {auth_callback.error}")
                    elif auth_callback.auth_code and auth_callback.state == state:
                        try:
                            account_info = minecraft_launcher_lib.microsoft_account.complete_login(
                                self.client_id, None, self.redirect_url, auth_callback.auth_code, code_verifier
                            )
                            if on_success: on_success(account_info)
                        except Exception as e:
                            if on_error: on_error(str(e))
                    else:
                        if on_error: on_error("Invalid state - possible CSRF")
                else:
                    if on_error: on_error("Timeout")
            finally:
                if self.server:
                    self.server.shutdown()
                    self.server.server_close()
        
        threading.Thread(target=wait_for_callback, daemon=True).start()
        return {"status": "success", "message": "Browser opened"}
    
    def refresh_login(self, refresh_token, on_success=None, on_error=None):
        def do_refresh():
            try:
                account_info = minecraft_launcher_lib.microsoft_account.complete_refresh(
                    self.client_id, None, self.redirect_url, refresh_token
                )
                if on_success: on_success(account_info)
            except Exception as e:
                if on_error: on_error(str(e))
        
        threading.Thread(target=do_refresh, daemon=True).start()