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
_ENCRYPTED_CLIENT_ID = "gAAAAABpdO_q5qoHo3fT_SbYss7SJVDZDEaf9mLdgO55nRECs8t0WhAufX3R183g5f57-NSRRgDLD5T6kY0eecUF8357H6JIy0qeqvJLUGWxJnwV7b6ObGS7a1Hx3jg5nEqkOQosD2Lk"
_ENCRYPTION_KEY = "yJBelSxAKQCF-NFJIvXStLt7zpdj_uJ0fMEm07C1hO8="


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


def get_client_id() -> str | None:
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
    
    return None


def clear_stored_credentials():
    if KEYRING_AVAILABLE:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_CLIENT_ID_KEY)
        except Exception:
            pass
