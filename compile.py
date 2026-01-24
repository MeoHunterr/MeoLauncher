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

# Ensure we are in the project root so .env can be found
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Load environment variables from .env in the project root
env_path = BASE_DIR / '.env'
print(f"Loading .env from: {env_path}")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("[OK] .env file found and loaded.")
else:
    print("[!] WARNING: .env file NOT found at expected path.")

# ==== SECURE CLIENT_ID EMBEDDING (AES-128) ====
def embed_client_id():
    """Embed encrypted CLIENT_ID into credentials.py before build."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("[!] Error: 'cryptography' module not found. Install it with: pip install cryptography")
        sys.exit(1)

    client_id = os.getenv("CLIENT_ID")
    if not client_id:
        print(f"[!] WARNING: CLIENT_ID not found in environment. Current keys: {list(os.environ.keys())}")
        print("[!] WARNING: CLIENT_ID not found in .env - production builds will require .env file")
        return
    
    # Generate Key and Encrypt
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_id = f.encrypt(client_id.encode()).decode()
    key_str = key.decode()
    
    credentials_path = os.path.join("app", "core", "credentials.py")
    
    if os.path.exists(credentials_path):
        with open(credentials_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace placeholders
        new_content = content.replace(
            '_ENCRYPTED_CLIENT_ID = ""',
            f'_ENCRYPTED_CLIENT_ID = "{encrypted_id}"'
        ).replace(
            '_ENCRYPTION_KEY = ""',
            f'_ENCRYPTION_KEY = "{key_str}"'
        )
        
        with open(credentials_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"[OK] CLIENT_ID encrypted with AES-128 and embedded.")
    else:
        print(f"[!] WARNING: {credentials_path} not found")

# ==== TEMPLATE RENDERING ====
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

# Run pre-build tasks
embed_client_id()
render_templates()

# Adjust paths to use obfuscated code in 'dist/app'
# We need to make sure cx_Freeze picks up the obfuscated files
# The simplest way is to temporarily swap directories or point include_files to dist/app
# But 'script' in Executable needs to point to the entry point.

# Strategy: Use 'app/webview_app.py' as script
SCRIPT_PATH = "app/webview_app.py"


# App metadata
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


# Files to include in the build
additional_files = []

# Frontend assets (HTML/CSS/JS) - includes docs folder with .md files
additional_files += include_files("app/assets", "lib/app/assets/")

# Explicitly ensure docs are included (redundant but safe)
if os.path.exists("app/assets/docs"):
    print("[*] Including documentation files (.md)")
    additional_files += include_files("app/assets/docs", "lib/app/assets/docs/")

# Game assets (required for playing)
if os.path.exists("app/game"):
    additional_files += include_files("app/game", "app/game/")

# Java runtime (required for playing)
if os.path.exists("app/java_pkg"):
    additional_files += include_files("app/java_pkg", "app/java_pkg/")

# Compressed assets (if using tar.xz method)
if os.path.exists("assets"):
    additional_files += include_files("assets", "assets/")

# Data folder (settings, etc.)
if os.path.exists("data"):
    additional_files += include_files("data", "data/")

# .env file (for CLIENT_ID)
# .env file - EXCLUDED for security


# Executable configuration
executables = [
    Executable(
        script=SCRIPT_PATH,
        base="Win32GUI",  # No console window
        target_name="MeoLauncher.exe",
        icon="app/assets/icon.ico" if os.path.exists("app/assets/icon.ico") else None
    )
]

# Build configuration
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
        "cryptography",    # Required for AES
        "psutil",          # Required for RAM detection
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
