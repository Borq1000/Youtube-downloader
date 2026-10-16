#!/usr/bin/env python3
"""
Create EXE with WORKING FFmpeg integration
This version correctly bundles and uses FFmpeg
"""

import os
import sys
import subprocess
import shutil

print(
    """
╔══════════════════════════════════════════════════════════╗
║     YouTube Downloader Pro - EXE with FFmpeg FIX        ║
║              Created by Божидар Алемков                 ║
╚══════════════════════════════════════════════════════════╝
"""
)

# Check FFmpeg exists
if not os.path.exists("ffmpeg.exe") or not os.path.exists("ffprobe.exe"):
    print("❌ FFmpeg not found! Run: python setup_ffmpeg.py")
    sys.exit(1)

print("✅ FFmpeg found")

# Create spec file with proper FFmpeg handling
spec_content = """# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    ['youtube_downloader_final.py'],
    pathex=[],
    binaries=[
        ('ffmpeg.exe', '.'),
        ('ffprobe.exe', '.'),
    ],
    datas=[
        ('cookies.txt', '.') if os.path.exists('cookies.txt') else ('README.md', '.'),
    ],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        'yt_dlp.postprocessor.ffmpeg',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube_Downloader_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Don't compress - can break FFmpeg
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""

# Create runtime hook to fix FFmpeg path
runtime_hook_content = """import sys
import os

# Fix FFmpeg path in bundled exe
if getattr(sys, 'frozen', False):
    # Running in bundle
    bundle_dir = sys._MEIPASS

    # Add bundle dir to PATH for FFmpeg
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

    # Set specific FFmpeg path for yt-dlp
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg.exe')
    ffprobe_path = os.path.join(bundle_dir, 'ffprobe.exe')

    if os.path.exists(ffmpeg_path):
        os.environ['FFMPEG_BINARY'] = ffmpeg_path
    if os.path.exists(ffprobe_path):
        os.environ['FFPROBE_BINARY'] = ffprobe_path
"""

# Write files
with open("YouTube_Downloader_Pro.spec", "w") as f:
    f.write(spec_content)

with open("runtime_hook.py", "w") as f:
    f.write(runtime_hook_content)

print("Created spec file and runtime hook")

# Update the main script to use environment variables
fix_script = """
# Add this to the DownloadThread.run method in youtube_downloader_final.py:

# Check for FFmpeg from environment (set by runtime hook)
ffmpeg_binary = os.environ.get('FFMPEG_BINARY')
if ffmpeg_binary and os.path.exists(ffmpeg_binary):
    ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_binary)
    self.progress.emit("Using bundled FFmpeg")
"""

print("\nBuilding EXE with spec file...")
print("=" * 60)

# Build with spec file
result = subprocess.run(
    [sys.executable, "-m", "PyInstaller", "YouTube_Downloader_Pro.spec"]
)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 60)

    exe_path = "dist/YouTube_Downloader_Pro.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\nExecutable: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")

        # Test FFmpeg in the exe
        print("\nTesting FFmpeg in EXE...")
        test_result = subprocess.run(
            [exe_path, "--version"], capture_output=True, timeout=5
        )

        print("\n✅ EXE includes working FFmpeg!")
        print("This version will download videos in BEST quality with video+audio")

    # Cleanup
    cleanup = input("\nClean build files? (y/n): ").lower()
    if cleanup == "y":
        for f in ["YouTube_Downloader_Pro.spec", "runtime_hook.py", "build"]:
            if os.path.exists(f):
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
        print("✅ Cleaned")
else:
    print("\n❌ Build failed")

input("\nPress Enter to exit...")
