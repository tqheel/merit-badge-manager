#!/bin/bash
# Setup script for Merit Badge Manager
# This script creates and activates the virtual environment

echo "Merit Badge Manager - Environment Setup"
echo "======================================"

# Check if we're in the project root
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    # Try to use python3.12 first, fall back to python3
    if command -v python3.12 &> /dev/null; then
        echo "🔍 Found Python 3.12, using it for virtual environment"
        python3.12 -m venv venv
    else
        echo "⚠️  Python 3.12 not found, using system python3"
        python3 -m venv venv
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Verify Python version (should be 3.12)
PYTHON_VERSION=$(python --version 2>&1)
echo "📋 Using Python: $PYTHON_VERSION"

# Check if we're using the wrong Python version
if [[ "$PYTHON_VERSION" == *"3.13"* ]]; then
    echo "⚠️  Warning: Using Python 3.13. Project requires Python 3.12"
    echo "💡 Consider installing Python 3.12 and recreating the virtual environment"
elif [[ "$PYTHON_VERSION" == *"3.12"* ]]; then
    echo "✅ Correct Python version (3.12) detected"
else
    echo "⚠️  Warning: Using Python version other than 3.12"
fi

# Check if activation was successful
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade dependencies
echo "📦 Installing/upgrading dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure GitHub token: cp .env.template .env"
echo "2. Start the server: python start_server.py"
echo ""
echo "💡 Remember to activate the virtual environment in new terminal sessions:"
echo "   source venv/bin/activate"
