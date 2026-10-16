#!/usr/bin/env python3
"""
Install PyInstaller and required packages for building exe
"""

import subprocess
import sys

print("Installing packages for EXE creation...")
print("=" * 60)

packages = [
    "pyinstaller",
    "pyinstaller-hooks-contrib",
    "pillow",  # For icon support
]

for package in packages:
    print(f"\nInstalling {package}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")

print("\n" + "=" * 60)
print("✅ Installation complete!")
print("\nNow run: python create_exe.py")

input("\nPress Enter to exit...")
