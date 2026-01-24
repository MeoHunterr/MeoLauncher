@echo off
echo ========================================
echo  MeoLauncher - Windows Build Script
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo [1/4] Installing dependencies...
pip install cx_Freeze pywebview msal requests python-dotenv pyarmor cryptography --quiet

:: Clean previous build
echo [2/4] Cleaning previous builds...
if exist "output-build" rmdir /s /q "output-build"
if exist "dist" rmdir /s /q "dist"

:: Run build (includes PyArmor obfuscation)
echo [3/4] Running PyArmor obfuscation...
echo [4/4] Building executable...
python compile.py build

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the output above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build completed successfully!
echo  Output: output-build\MeoLauncher.exe
echo ========================================
pause
