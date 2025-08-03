#!/usr/bin/env python3
"""
Startup script for the Merit Badge Manager MCP Server.
Ensures virtual environment is set up and activated before starting.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_virtual_environment():
    """Set up and activate Python virtual environment."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("📦 Creating Python virtual environment...")
        
        # Try to use python3.12 first, fall back to python3
        python_cmd = None
        if shutil.which("python3.12"):
            python_cmd = "python3.12"
            print("🔍 Found Python 3.12, using it for virtual environment")
        elif shutil.which("python3"):
            python_cmd = "python3"
            print("⚠️  Python 3.12 not found, using system python3")
        else:
            raise RuntimeError("No suitable Python interpreter found")
        
        subprocess.run([python_cmd, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    
    # Determine the activation script path based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate"
        python_executable = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        activate_script = venv_path / "bin" / "activate"
        python_executable = venv_path / "bin" / "python"
    
    if not python_executable.exists():
        raise RuntimeError("Virtual environment setup failed - Python executable not found")
    
    # Check Python version
    try:
        result = subprocess.run([str(python_executable), "--version"], 
                              capture_output=True, text=True)
        python_version = result.stdout.strip()
        print(f"📋 Using {python_version}")
        
        # Warn if not using Python 3.12
        if "3.12" in python_version:
            print("✅ Correct Python version (3.12) detected")
        elif "3.13" in python_version:
            print("⚠️  Warning: Using Python 3.13. Project recommends Python 3.12")
        else:
            print("⚠️  Warning: Using Python version other than 3.12")
    except Exception as e:
        print(f"⚠️  Could not check Python version: {e}")
    
    return str(python_executable)

def check_dependencies(python_executable):
    """Check if required dependencies are installed in the virtual environment."""
    try:
        result = subprocess.run([
            python_executable, "-c", 
            "import fastapi, uvicorn, yaml, aiohttp, aiofiles, pydantic"
        ], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_configuration():
    """Check if GitHub configuration is set up."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("⚠️  GitHub token not configured. Set GITHUB_TOKEN environment variable.")
        return False
    return True

def main():
    """Main startup function."""
    print("Merit Badge Manager - MCP Server Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("mcp-server/main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Set up virtual environment
    print("� Setting up Python virtual environment...")
    try:
        python_executable = setup_virtual_environment()
        print(f"✅ Using Python: {python_executable}")
    except Exception as e:
        print(f"❌ Failed to set up virtual environment: {e}")
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies(python_executable):
        print("\n💡 Installing dependencies...")
        try:
            subprocess.run([
                python_executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    else:
        print("✅ All dependencies are installed")
    
    # Check configuration
    print("\n🔧 Checking configuration...")
    config_ok = check_configuration()
    if not config_ok:
        print("⚠️  GitHub integration will be limited without proper configuration")
        print("💡 Copy .env.template to .env and add your GitHub token")
    
    # Start the server
    print("\n🚀 Starting MCP Server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API documentation at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Convert to absolute path before changing directories
        python_executable = os.path.abspath(python_executable)
        
        # Change to mcp-server directory and start uvicorn
        os.chdir("mcp-server")
        subprocess.run([
            python_executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
