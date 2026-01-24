import requests
import uuid as uuid_lib
import json
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ElybyAuthError(Exception):
    pass


class ElybyTwoFactorRequired(ElybyAuthError):
    pass


class ElybyAuth:
    AUTH_SERVER = "https://authserver.ely.by"
    
    def __init__(self, data_dir: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "User-Agent": "MeoLauncher/1.0"})
        self.data_dir = data_dir
        self.credentials_file = os.path.join(data_dir, "elyby_credentials.json") if data_dir else None
        self.client_token = self._load_or_generate_client_token()
        self.access_token: Optional[str] = None
        self.uuid: Optional[str] = None
        self.username: Optional[str] = None
        self._load_credentials()
    
    def _load_or_generate_client_token(self) -> str:
        if self.credentials_file and os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    return json.load(f).get("client_token", str(uuid_lib.uuid4()))
            except (json.JSONDecodeError, IOError, OSError) as e:
                logger.debug("Failed to load client token: %s", e)
        return str(uuid_lib.uuid4())
    
    def _load_credentials(self):
        if self.credentials_file and os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.uuid = data.get("uuid")
                    self.username = data.get("username")
            except (json.JSONDecodeError, IOError, OSError) as e:
                logger.debug("Failed to load credentials: %s", e)
    
    def _save_credentials(self):
        if self.credentials_file:
            try:
                os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
                with open(self.credentials_file, 'w') as f:
                    json.dump({
                        "client_token": self.client_token,
                        "access_token": self.access_token,
                        "uuid": self.uuid,
                        "username": self.username
                    }, f)
            except (IOError, OSError) as e:
                logger.debug("Failed to save credentials: %s", e)
    
    def authenticate(self, username: str, password: str, totp_token: Optional[str] = None) -> Dict:
        actual_password = f"{password}:{totp_token}" if totp_token else password
        
        payload = {
            "username": username,
            "password": actual_password,
            "clientToken": self.client_token,
            "requestUser": True
        }
        
        try:
            resp = self.session.post(f"{self.AUTH_SERVER}/auth/authenticate", json=payload, timeout=15)
            data = resp.json()
            
            if resp.status_code == 200:
                self.access_token = data["accessToken"]
                self.uuid = data["selectedProfile"]["id"]
                self.username = data["selectedProfile"]["name"]
                self._save_credentials()
                return {"username": self.username, "uuid": self.uuid, "access_token": self.access_token, "source": "elyby"}
            
            if resp.status_code == 401:
                error_msg = data.get("errorMessage", "")
                if "two factor" in error_msg.lower():
                    raise ElybyTwoFactorRequired("2FA required")
                raise ElybyAuthError(f"Auth failed: {error_msg}")
            
            raise ElybyAuthError(f"Auth failed: {data.get('errorMessage', resp.text)}")
                
        except requests.RequestException as e:
            raise ElybyAuthError(f"Network error: {e}")
    
    def refresh(self) -> bool:
        if not self.access_token:
            return False
        
        try:
            resp = self.session.post(
                f"{self.AUTH_SERVER}/auth/refresh",
                json={"accessToken": self.access_token, "clientToken": self.client_token, "requestUser": True},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data["accessToken"]
                self.uuid = data["selectedProfile"]["id"]
                self.username = data["selectedProfile"]["name"]
                self._save_credentials()
                return True
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            logger.debug("Token refresh failed: %s", e)
        self.access_token = None
        return False
    
    def validate(self) -> bool:
        if not self.access_token:
            return False
        try:
            resp = self.session.post(
                f"{self.AUTH_SERVER}/auth/validate",
                json={"accessToken": self.access_token, "clientToken": self.client_token},
                timeout=10
            )
            return resp.status_code in (200, 204)
        except requests.RequestException as e:
            logger.debug("Token validation failed: %s", e)
            return False
    
    def signout(self, username: str, password: str) -> bool:
        try:
            resp = self.session.post(
                f"{self.AUTH_SERVER}/auth/signout",
                json={"username": username, "password": password},
                timeout=15
            )
            if resp.status_code in (200, 204):
                self.access_token = self.uuid = self.username = None
                self._save_credentials()
                return True
        except requests.RequestException as e:
            logger.debug("Signout failed: %s", e)
        return False
    
    def get_session_info(self) -> Optional[Dict]:
        if self.access_token and self.username and self.uuid:
            return {"username": self.username, "uuid": self.uuid, "access_token": self.access_token, "source": "elyby"}
        return None
    
    def ensure_valid_session(self) -> bool:
        return self.validate() or self.refresh()


def create_offline_session(username: str) -> Dict:
    offline_uuid = str(uuid_lib.uuid3(uuid_lib.NAMESPACE_DNS, f"OfflinePlayer:{username}"))
    return {"username": username, "uuid": offline_uuid.replace("-", ""), "access_token": "0", "source": "offline"}
