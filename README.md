# BTA Launcher (v2.0)

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, lightweight launcher for **Better Than Adventure (b1.7.3 Modpack)**. Built with Python and PyWebview, featuring a sleek modern UI.

## ✨ Features

- **Modern UI**: modern launchers-style dark theme with glassmorphism effects.
- **Microsoft Login**: Secure device code authentication flow.
- **Offline Mode**: Play without a Microsoft account.
- **Deep Settings**: RAM, Resolution, Java Path, JVM optimization.
- **Quick Access**: Screenshots & Texture Packs folders.
- **Auto Java**: Bundled Java runtime for instant play.

## 🚀 Quick Start

### Run from Source
```bash
pip install -r requirements.txt
python app/webview_app.py
```

## 🛠️ Build

### Compile to EXE
```bash
compile-windows.bat
```
Output: `output-build/BTA Launcher.exe`

### Create Installer (Optional)
1. Install [NSIS](https://nsis.sourceforge.io/)
2. Open NSIS → "Compile NSI scripts"
3. Load `installer/compile.nsi` (or `compile-compress.nsi` for smaller size)
4. Run the generated `BTA Launcher Setup.exe`

## 📂 Project Structure

```
bta-launcher/
├── app/
│   ├── assets/        # HTML/CSS/JS Frontend
│   ├── core/          # Logic (Java, Launch, Settings, Auth)
│   ├── game/          # Minecraft Assets
│   ├── java_pkg/      # Java Runtime
│   └── webview_app.py # Main Entry Point
├── installer/         # NSIS Scripts
├── compile.py         # cx_Freeze Build Script
├── compile-windows.bat
├── requirements.txt
└── README.md
```

## 🤝 Credits

- **Better Than Adventure** Team for the modpack.
- **PyWebview** for the desktop UI framework.
- **modern launchers** for UI inspiration.
