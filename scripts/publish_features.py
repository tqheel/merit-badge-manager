#!/usr/bin/env python3
"""
Example script demonstrating how to publish feature requests to GitHub.
Ensures virtual environment is activated before running.
"""

import asyncio
import sys
import os
from pathlib import Path

# Ensure we're using the virtual environment Python
def ensure_venv():
    """Ensure we're running in the virtual environment."""
    venv_path = Path(__file__).parent.parent / "venv"
    
    if os.name == 'nt':  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        venv_python = venv_path / "bin" / "python"
    
    if venv_path.exists() and venv_python.exists():
        current_python = sys.executable
        if str(venv_python) not in current_python:
            print("⚠️  Not running in virtual environment!")
            print(f"Please activate the virtual environment first:")
            if os.name == 'nt':
                print("  venv\\Scripts\\activate")
            else:
                print("  source venv/bin/activate")
            print(f"Then run: python {__file__}")
            sys.exit(1)
        else:
            print(f"✅ Using virtual environment: {current_python}")
    else:
        print("⚠️  Virtual environment not found!")
        print("Please run the setup first: ./setup.sh")
        sys.exit(1)

# Check virtual environment first
ensure_venv()

# Now import the dependencies (they should be available in venv)
try:
    import aiohttp
    import json
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Configuration
MCP_SERVER_URL = "http://127.0.0.1:8000"

async def list_unpublished_features():
    """List all unpublished feature files."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{MCP_SERVER_URL}/features") as response:
            if response.status == 200:
                data = await response.json()
                return data["features"]
            else:
                print(f"Error listing features: {response.status}")
                return []

async def publish_feature(yml_filename):
    """Publish a specific feature to GitHub."""
    payload = {"yml_filename": yml_filename}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{MCP_SERVER_URL}/publish-feature",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Successfully published {yml_filename}")
                print(f"   GitHub Issue: {data['github_issue']['url']}")
                print(f"   Issue Number: #{data['github_issue']['number']}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Failed to publish {yml_filename}: {error_text}")
                return False

async def main():
    """Main function to demonstrate the publishing workflow."""
    print("Merit Badge Manager - Feature Publisher")
    print("=" * 50)
    
    # List unpublished features
    print("📋 Listing unpublished features...")
    features = await list_unpublished_features()
    
    if not features:
        print("No unpublished features found.")
        return
    
    print(f"Found {len(features)} unpublished features:")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")
    
    print("\n🚀 Publishing features to GitHub...")
    
    # Publish each feature
    for feature in features:
        print(f"\nPublishing {feature}...")
        success = await publish_feature(feature)
        if success:
            # Small delay between requests to be nice to GitHub API
            await asyncio.sleep(1)
    
    print("\n✨ Publishing complete!")

if __name__ == "__main__":
    asyncio.run(main())
