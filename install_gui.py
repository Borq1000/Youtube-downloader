#!/usr/bin/env python3
"""
Install PyQt6 for the GUI application
"""

import subprocess
import sys

print("Installing PyQt6 for YouTube Downloader GUI...")
print("=" * 50)

packages = ["PyQt6", "PyQt6-Qt6", "PyQt6-sip"]

for package in packages:
    print(f"\nInstalling {package}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
            print(result.stderr)
    except Exception as e:
        print(f"✗ Error installing {package}: {e}")

print("\n" + "=" * 50)
print("Installation complete!")
print("\nTo run the GUI application:")
print("  python youtube_gui.py")

input("\nPress Enter to exit...")
