"""
Build script for MeoLauncher using cx_Freeze + PyArmor.
Produces a standalone Windows executable with obfuscated code.

Usage:
    python compile.py build
"""

from cx_Freeze import setup, Executable
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

env_path = BASE_DIR / '.env'
print(f"Loading .env from: {env_path}")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("[OK] .env file found and loaded.")
else:
    print("[!] WARNING: .env file NOT found at expected path.")

import re
import shutil
import atexit

_CREDENTIALS_PATH = os.path.join("app", "core", "credentials.py")
_CREDENTIALS_BACKUP = None

def embed_client_id():
    """Embed encrypted CLIENT_ID into credentials.py before build."""
    global _CREDENTIALS_BACKUP
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("[!] Error: 'cryptography' module not found. Install it with: pip install cryptography")
        sys.exit(1)

    client_id = os.getenv("CLIENT_ID")
    if not client_id:
        print(f"[!] WARNING: CLIENT_ID not found in .env file!")
        print(f"[!] Microsoft login will be disabled. Only Ely.by and offline login available.")
        return  # Skip embedding, don't fail the build
    
    if not os.path.exists(_CREDENTIALS_PATH):
        print(f"[!] ERROR: {_CREDENTIALS_PATH} not found")
        sys.exit(1)
    
    _CREDENTIALS_BACKUP = _CREDENTIALS_PATH + ".backup"
    shutil.copy2(_CREDENTIALS_PATH, _CREDENTIALS_BACKUP)
    atexit.register(restore_credentials_py)
    
    with open(_CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_id = fernet.encrypt(client_id.encode()).decode()
    key_str = key.decode()
    
    new_content = re.sub(
        r'_ENCRYPTED_CLIENT_ID\s*=\s*"[^"]*"',
        f'_ENCRYPTED_CLIENT_ID = "{encrypted_id}"',
        content
    )
    new_content = re.sub(
        r'_ENCRYPTION_KEY\s*=\s*"[^"]*"',
        f'_ENCRYPTION_KEY = "{key_str}"',
        new_content
    )
    
    with open(_CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"[OK] CLIENT_ID encrypted with Fernet and embedded into credentials.py")
    print(f"[OK] Client ID: {client_id[:8]}...{client_id[-4:]}")


def restore_credentials_py():
    """Restore original credentials.py after build (removes embedded secrets)."""
    global _CREDENTIALS_BACKUP
    if _CREDENTIALS_BACKUP and os.path.exists(_CREDENTIALS_BACKUP):
        shutil.move(_CREDENTIALS_BACKUP, _CREDENTIALS_PATH)
        print("[OK] credentials.py restored to original state")
        _CREDENTIALS_BACKUP = None


def render_templates():
    """Render Jinja2 templates to HTML before build."""
    try:
        sys.path.append(str(BASE_DIR / "app"))
        from template_renderer import render_index
        
        print("[*] Pre-rendering Jinja2 templates...")
        html_content = render_index()
        
        output_path = BASE_DIR / "app" / "assets" / "index.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"[OK] Templates rendered to {output_path}")
    except Exception as e:
        print(f"[!] WARNING: Failed to render templates: {e}")
        print("    Build will proceed with existing index.html")

embed_client_id()
render_templates()

SCRIPT_PATH = "app/webview_app.py"

APP_NAME = "MeoLauncher"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "MeoLauncher - Minecraft BTA Modpack Launcher"


def include_files(source_folder, target_folder):
    """Recursively include all files from a folder."""
    files = []
    if not os.path.exists(source_folder):
        return files
    for root, _, filenames in os.walk(source_folder):
        for filename in filenames:
            source_path = os.path.join(root, filename)
            relative_path = os.path.relpath(source_path, source_folder)
            target_path = os.path.join(target_folder, relative_path)
            files.append((source_path, target_path))
    return files


additional_files = []

additional_files += include_files("app/assets", "lib/app/assets/")

if os.path.exists("app/assets/docs"):
    print("[*] Including documentation files (.md)")
    additional_files += include_files("app/assets/docs", "lib/app/assets/docs/")

if os.path.exists("app/game"):
    additional_files += include_files("app/game", "app/game/")

if os.path.exists("app/java_pkg"):
    additional_files += include_files("app/java_pkg", "app/java_pkg/")

if os.path.exists("assets"):
    additional_files += include_files("assets", "assets/")

if os.path.exists("data"):
    additional_files += include_files("data", "data/")

executables = [
    Executable(
        script=SCRIPT_PATH,
        base="gui", 
        target_name="MeoLauncher.exe",
        icon="app/assets/icon.ico" if os.path.exists("app/assets/icon.ico") else None
    )
]

build_options = {
    "packages": [
        "webview",
        "msal",
        "requests",
        "dotenv",
        "json",
        "os",
        "sys",
        "threading",
        "subprocess",
        "hashlib",
        "uuid",
        "tarfile",
        "ctypes",
        "urllib",
        "pathlib",
        "http",
        "html",
        "wsgiref",
        "bottle",
        "ssl",
        "certifi",
        "cryptography",  
        "psutil",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "pydoc",
        "doctest",
        "argparse",
        "difflib",
        "asyncio",
        "multiprocessing",
        "test",
    ],
    "include_files": additional_files,
    "build_exe": "output-build",
    "include_msvcr": True,
}

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    options={"build_exe": build_options},
    executables=executables,
)
