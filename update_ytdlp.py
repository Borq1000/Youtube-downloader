#!/usr/bin/env python3
"""
Script to update yt-dlp to the latest version
"""

import subprocess
import sys

print("Updating yt-dlp to the latest version...")
print("-" * 50)

try:
    # Try to update yt-dlp
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✓ yt-dlp successfully updated!")
        print("\nOutput:", result.stdout)
    else:
        print("✗ Error updating yt-dlp:")
        print(result.stderr)

    # Check version
    print("\nChecking yt-dlp version...")
    result = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--version"], capture_output=True, text=True
    )
    print("Current version:", result.stdout.strip())

except Exception as e:
    print(f"Error: {e}")
    print("\nTry running manually:")
    print("pip install --upgrade yt-dlp")

input("\nPress Enter to exit...")
