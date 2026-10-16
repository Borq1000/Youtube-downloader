#!/usr/bin/env python3
"""
Build standalone .exe for YouTube Downloader Pro
Includes all dependencies and FFmpeg
"""

import os
import sys
import subprocess
import shutil


def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller

        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ PyInstaller installed successfully")
            return True
        else:
            print("❌ Failed to install PyInstaller")
            print(result.stderr)
            return False


def setup_ffmpeg():
    """Ensure FFmpeg is available"""
    if not os.path.exists("ffmpeg.exe") or not os.path.exists("ffprobe.exe"):
        print("\n⚠️ FFmpeg not found. Setting up FFmpeg...")
        subprocess.run([sys.executable, "setup_ffmpeg.py"])
    else:
        print("✅ FFmpeg found")


def create_spec_file():
    """Create PyInstaller spec file with all settings"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['youtube_downloader_final.py'],
    pathex=[],
    binaries=[
        ('ffmpeg.exe', '.'),
        ('ffprobe.exe', '.'),
    ],
    datas=[
        ('cookies.txt', '.') if os.path.exists('cookies.txt') else ('', ''),
    ],
    hiddenimports=['yt_dlp', 'PyQt6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YouTube_Downloader_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version.txt' if os.path.exists('version.txt') else None,
)
"""

    with open("youtube_downloader.spec", "w") as f:
        f.write(spec_content)

    print("✅ Spec file created")


def create_version_file():
    """Create version information file"""
    version_content = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Божидар Алемков'),
        StringStruct(u'FileDescription', u'YouTube Downloader Pro'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'YouTube_Downloader_Pro'),
        StringStruct(u'LegalCopyright', u'© 2024 Божидар Алемков'),
        StringStruct(u'OriginalFilename', u'YouTube_Downloader_Pro.exe'),
        StringStruct(u'ProductName', u'YouTube Downloader Pro'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    with open("version.txt", "w", encoding="utf-8") as f:
        f.write(version_content)

    print("✅ Version file created")


def build_exe():
    """Build the executable"""
    print("\n" + "=" * 60)
    print("Building YouTube Downloader Pro.exe...")
    print("=" * 60)

    # Install PyInstaller
    if not install_pyinstaller():
        return False

    # Setup FFmpeg
    setup_ffmpeg()

    # Create version file
    create_version_file()

    # Create spec file
    create_spec_file()

    # Build using PyInstaller
    print("\nBuilding executable...")
    print("This may take several minutes...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        "YouTube_Downloader_Pro",
        "--add-binary",
        "ffmpeg.exe;.",
        "--add-binary",
        "ffprobe.exe;.",
        "--hidden-import",
        "yt_dlp",
        "--hidden-import",
        "PyQt6",
        "youtube_downloader_final.py",
    ]

    # Add cookies if exists
    if os.path.exists("cookies.txt"):
        cmd.extend(["--add-data", "cookies.txt;."])

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ Build successful!")
        print(f"Executable location: dist/YouTube_Downloader_Pro.exe")
        print("=" * 60)

        # Create distribution folder
        dist_folder = "YouTube_Downloader_Pro_Distribution"
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        os.makedirs(dist_folder)

        # Copy exe to distribution folder
        shutil.copy2("dist/YouTube_Downloader_Pro.exe", dist_folder)

        # Create README
        readme_content = """
YouTube Downloader Pro
Created by Божидар Алемков

INSTALLATION:
1. Run YouTube_Downloader_Pro.exe
2. No installation required - portable application

HOW TO USE:
1. Get cookies from YouTube using Chrome extension
2. Paste cookies in Settings tab
3. Enter YouTube URL
4. Click Download

FEATURES:
- Download videos in best quality
- Extract audio to MP3
- Support for playlists
- Multi-language support (English/Russian)
- FFmpeg included for best quality

REQUIREMENTS:
- Windows 10 or later
- Internet connection
"""

        with open(f"{dist_folder}/README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"\n✅ Distribution package created: {dist_folder}/")
        print("   - YouTube_Downloader_Pro.exe")
        print("   - README.txt")

        return True
    else:
        print("\n❌ Build failed")
        return False


def main():
    print("YouTube Downloader Pro - EXE Builder")
    print("Created by Божидар Алемков")
    print("=" * 60)

    # Check if main script exists
    if not os.path.exists("youtube_downloader_final.py"):
        print("❌ youtube_downloader_final.py not found!")
        print("Make sure you're running this script in the correct directory")
        input("\nPress Enter to exit...")
        return

    # Build executable
    if build_exe():
        print("\n✅ Everything complete!")
        print("\nYou can now distribute the YouTube_Downloader_Pro.exe file")
        print("It includes all dependencies and FFmpeg")
    else:
        print("\n❌ Build process failed")
        print("Please check the error messages above")

    # Clean up build files
    clean = input("\nClean up build files? (y/n): ").lower()
    if clean == "y":
        dirs_to_remove = ["build", "__pycache__"]
        files_to_remove = ["youtube_downloader.spec", "version.txt"]

        for dir_name in dirs_to_remove:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"Removed {dir_name}/")

        for file_name in files_to_remove:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"Removed {file_name}")

        print("✅ Cleanup complete")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
