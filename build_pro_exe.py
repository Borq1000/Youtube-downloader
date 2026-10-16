#!/usr/bin/env python3
"""
Build YouTube Downloader Pro as a standalone .exe
Bundles FFmpeg for best quality video+audio merging.
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile

print("")
print("=" * 58)
print("    YouTube Downloader Pro - EXE Builder")
print("=" * 58)

# Step 1: Check dependencies
print("\n1. Checking dependencies...")

try:
    import PyInstaller
    print("   [OK] PyInstaller found")
except ImportError:
    print("   Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("   [OK] PyInstaller installed")

try:
    import yt_dlp
    print(f"   [OK] yt-dlp {yt_dlp.version.__version__}")
except ImportError:
    print("   [FAIL] yt-dlp not installed. Run: pip install yt-dlp")
    sys.exit(1)

try:
    import PyQt6
    print("   [OK] PyQt6 found")
except ImportError:
    print("   [FAIL] PyQt6 not installed. Run: pip install PyQt6")
    sys.exit(1)

# Step 2: Ensure FFmpeg is present
print("\n2. Checking FFmpeg...")
if not os.path.exists("ffmpeg.exe") or not os.path.exists("ffprobe.exe"):
    print("   FFmpeg not found. Downloading...")
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    try:
        urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")
        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("ffmpeg.exe"):
                    with zip_ref.open(file) as src, open("ffmpeg.exe", "wb") as dst:
                        dst.write(src.read())
                elif file.endswith("ffprobe.exe"):
                    with zip_ref.open(file) as src, open("ffprobe.exe", "wb") as dst:
                        dst.write(src.read())
        os.remove("ffmpeg.zip")
        print("   [OK] FFmpeg downloaded")
    except Exception as e:
        print(f"   [FAIL] Failed to download FFmpeg: {e}")
        print("   Download manually from https://ffmpeg.org/download.html")
        sys.exit(1)
else:
    print("   [OK] FFmpeg found")

# Step 3: Clean old builds
print("\n3. Cleaning old builds...")
for path in ["dist", "build", "YouTube_Downloader_Pro.spec"]:
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
print("   [OK] Clean")

# Step 4: Build with PyInstaller
print("\n4. Building EXE (this may take a few minutes)...")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "YouTube_Downloader_Pro",
    # Bundle FFmpeg
    "--add-binary", "ffmpeg.exe;.",
    "--add-binary", "ffprobe.exe;.",
    # Collect ALL of yt-dlp: every extractor, downloader, postprocessor and the
    # newer JS-challenge solver modules. Manual --hidden-import lists go stale as
    # yt-dlp evolves; --collect-all guarantees the frozen EXE matches the source.
    "--collect-all", "yt_dlp",
    # Hidden imports for PyQt6
    "--hidden-import", "PyQt6.sip",
]

# Add icon if exists
if os.path.exists("icon.ico"):
    cmd.extend(["--icon", "icon.ico", "--add-data", "icon.ico;."])

# Entry point
cmd.append("youtube_downloader_pro.py")

result = subprocess.run(cmd)

if result.returncode == 0:
    exe_path = os.path.join("dist", "YouTube_Downloader_Pro.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("")
        print("=" * 58)
        print("  BUILD SUCCESSFUL!")
        print("=" * 58)
        print(f"  File: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print("")
        print("  Features:")
        print("   - Video + audio up to 4K HDR")
        print("   - FFmpeg bundled")
        print("   - Proxy support")
        print("   - Auto browser cookie extraction")
        print("   - EN/RU interface")
        print("=" * 58)
    else:
        print("\n[FAIL] EXE not found after build")
else:
    print("\n[FAIL] Build failed. Check errors above.")

input("\nPress Enter to exit...")
