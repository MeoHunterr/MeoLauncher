import os
import base64
from dotenv import load_dotenv

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

load_dotenv()

KEYRING_SERVICE = "MeoLauncher"
KEYRING_CLIENT_ID_KEY = "client_id"
_ENCRYPTED_CLIENT_ID = ""
_ENCRYPTION_KEY = ""


def store_client_id(client_id: str) -> bool:
    if not KEYRING_AVAILABLE:
        return False
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_CLIENT_ID_KEY, client_id)
        return True
    except Exception:
        return False


def get_client_id_from_keyring() -> str | None:
    if not KEYRING_AVAILABLE:
        return None
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_CLIENT_ID_KEY)
    except Exception:
        return None


def get_client_id() -> str:
    keyring_id = get_client_id_from_keyring()
    if keyring_id:
        return keyring_id
    
    env_id = os.getenv("CLIENT_ID")
    if env_id:
        store_client_id(env_id)
        return env_id
    
    if _ENCRYPTED_CLIENT_ID and _ENCRYPTION_KEY and CRYPTO_AVAILABLE:
        try:
            f = Fernet(_ENCRYPTION_KEY.encode())
            client_id = f.decrypt(_ENCRYPTED_CLIENT_ID.encode()).decode('utf-8')
            store_client_id(client_id)
            return client_id
        except Exception:
            pass
    
    raise ValueError("CLIENT_ID not found. Set in .env or build with compile.py")


def clear_stored_credentials():
    if KEYRING_AVAILABLE:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_CLIENT_ID_KEY)
        except Exception:
            pass
