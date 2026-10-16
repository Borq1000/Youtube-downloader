#!/usr/bin/env python3
"""
Create EXE that actually works with video+audio
Uses formats that don't require FFmpeg merging
"""

import os
import sys
import subprocess
import shutil

print(
    """
╔══════════════════════════════════════════════════════════╗
║       YouTube Downloader Pro - SIMPLE EXE Builder       ║
║              Created by Божидар Алемков                 ║
╚══════════════════════════════════════════════════════════╝
"""
)

# Clean old builds
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

print("Building WORKING YouTube Downloader...")
print("This version downloads video+audio correctly!")
print("=" * 60)

# Simple PyInstaller command - no FFmpeg complexity
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--windowed",
    "--name",
    "YouTube_Downloader_Working",
]

# Add icon if exists
if os.path.exists("icon.ico"):
    cmd.extend(["--icon", "icon.ico"])

# Add cookies if exists
if os.path.exists("cookies.txt"):
    cmd.extend(["--add-data", "cookies.txt;."])

# Hidden imports
cmd.extend(
    [
        "--hidden-import",
        "yt_dlp",
        "--hidden-import",
        "PyQt6",
        "--clean",
        "youtube_downloader_fixed.py",  # Use the FIXED version
    ]
)

print("Running PyInstaller...")
result = subprocess.run(cmd)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 60)

    exe_path = "dist/YouTube_Downloader_Working.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\nExecutable: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")

        print("\n✨ This version:")
        print("  • Downloads videos WITH picture and sound")
        print("  • Uses YouTube formats that include both")
        print("  • No FFmpeg dependency issues")
        print("  • Works on any Windows 10+")
else:
    print("\n❌ Build failed")

input("\nPress Enter to exit...")
