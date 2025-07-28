@echo off
REM Setup script for Merit Badge Manager (Windows)
REM This script creates and activates the virtual environment

echo Merit Badge Manager - Environment Setup
echo ======================================

REM Check if we're in the project root
if not exist "requirements.txt" (
    echo ❌ Please run this script from the project root directory
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    REM Try to use python3.12 first, fall back to python
    where python3.12 >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo 🔍 Found Python 3.12, using it for virtual environment
        python3.12 -m venv venv
    ) else (
        echo ⚠️  Python 3.12 not found, using system python
        python -m venv venv
    )
    if %ERRORLEVEL% equ 0 (
        echo ✅ Virtual environment created
    ) else (
        echo ❌ Failed to create virtual environment
        exit /b 1
    )
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🐍 Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify Python version
echo 📋 Using Python:
python --version

REM Install/upgrade dependencies
echo 📦 Installing/upgrading dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Configure GitHub token: copy .env.template .env
echo 2. Start the server: python start_server.py
echo.
echo 💡 Remember to activate the virtual environment in new terminal sessions:
echo    venv\Scripts\activate
