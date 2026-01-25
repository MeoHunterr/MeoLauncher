# 🐱 MeoLauncher (v2.1)

[![Version](https://img.shields.io/badge/version-2.1.0-39d353?style=for-the-badge)](https://github.com/meohunterr/MeoLauncher)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey?style=for-the-badge)](https://www.microsoft.com/windows)

**MeoLauncher** is a high-performance, modern Minecraft launcher specifically optimized for **Better Than Adventure (BTA v7.3_04)**. Built with a focus on aesthetics, security, and performance.

---

## ✨ Key Features

### 🔐 Advanced Authentication
- **Microsoft OAuth2**: Secure login using the official Microsoft flow (Authorization Code + PKCE).
- **Ely.by Integration**: Full support for Ely.by accounts, skins, and capes.
- **Offline Mode**: Play instantly without an external account.

### 🎨 Premium User Experience
- **Modern UI**: Sleek dark theme with glassmorphism, vibrant accents, and smooth animations.
- **Skin System**: Automatic premium skin synchronization and Ely.by skin management.
- **Preview Grids**: Built-in gallery for screenshots and texture packs with thumbnails and management tools.
- **Multi-language**: Native support for **English** and **Vietnamese**.

### ⚡ Performance & Security
- **JVM Optimization**: Pre-configured performance profiles (G1GC, ParallelGC, etc.) to eliminate micro-stutters.
- **Advanced Anti-Cheat**: Real-time monitoring for unauthorized mods and X-Ray detection.
- **Resource Efficient**: Lightweight Python backend with a fast `pywebview` frontend.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Java Runtime Environment (bundled in release)

### Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/meohunterr/MeoLauncher.git
   cd MeoLauncher
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your `CLIENT_ID`:
   ```env
   CLIENT_ID=your_azure_client_id_here
   ```
4. Launch the app:
   ```bash
   python app/webview_app.py
   ```

---

## 🛠️ Build & Deployment

The launcher uses a multi-stage build process for maximum security and portability.

### 1. Compile to Executable
We use `cx_Freeze` combined with `PyArmor` for code protection.
```bash
python compile.py build
```
The output will be located in the `output-build/` directory.

### 2. Create Installer
Use the provided NSIS scripts in the `installer/` directory to generate a professional Windows installer.
- Requires [NSIS](https://nsis.sourceforge.io/) installed.
- Compile `installer/compile.nsi` for the standard setup.

---

## 📂 Project Structure

```text
MeoLauncher/
├── app/
│   ├── assets/         # Frontend (HTML, CSS, JS, Templates)
│   ├── core/           # Backend (Auth, Launcher, Skins, Anti-Cheat)
│   ├── game/           # Minecraft game files & assets
│   ├── java_pkg/       # Bundled Java Runtime
│   └── webview_app.py  # Application entry point
├── installer/          # NSIS installation scripts
├── compile.py          # Build & Encryption script
├── .env                # Environment variables (Secrets)
└── requirements.txt    # Python dependencies
```

---

## 🤝 Support & Contribution

If you find this project helpful, consider supporting its development:

- ⭐ **Star** the repository on GitHub.
- 🐛 **Report bugs** via the Issues tab.
- 🌐 **Translate** the launcher into more languages.

---

## 📜 Disclaimer

MeoLauncher is not affiliated with Mojang AB or Microsoft. Minecraft is a trademark of Mojang Synergies AB. This launcher is intended for use with the Better Than Adventure modpack.

**Developed with ❤️ by MeoHunterr**
