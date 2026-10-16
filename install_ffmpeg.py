#!/usr/bin/env python3
"""
Download and install FFmpeg for Windows
"""

import os
import sys
import subprocess
import zipfile
import urllib.request
import shutil


def download_ffmpeg():
    """Download FFmpeg for Windows"""
    print("Downloading FFmpeg for Windows...")
    print("=" * 50)

    # FFmpeg download URL (stable release)
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"

    try:
        # Download FFmpeg
        print(f"Downloading from: {url}")
        print("This may take a few minutes...")
        urllib.request.urlretrieve(url, zip_path)
        print("✓ Download complete")

        # Extract FFmpeg
        print("\nExtracting FFmpeg...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(".")
        print("✓ Extraction complete")

        # Find the extracted folder
        extracted_folder = None
        for item in os.listdir("."):
            if item.startswith("ffmpeg-") and os.path.isdir(item):
                extracted_folder = item
                break

        if not extracted_folder:
            print("✗ Could not find extracted FFmpeg folder")
            return False

        # Copy FFmpeg executables to current directory
        bin_path = os.path.join(extracted_folder, "bin")
        if os.path.exists(bin_path):
            for exe in ["ffmpeg.exe", "ffprobe.exe", "ffplay.exe"]:
                src = os.path.join(bin_path, exe)
                dst = exe
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"✓ Copied {exe}")

        # Clean up
        print("\nCleaning up...")
        os.remove(zip_path)
        shutil.rmtree(extracted_folder)
        print("✓ Cleanup complete")

        # Test FFmpeg
        print("\nTesting FFmpeg...")
        result = subprocess.run(
            ["ffmpeg.exe", "-version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ FFmpeg is working!")
            version_line = result.stdout.split("\n")[0]
            print(f"Version: {version_line}")
            return True
        else:
            print("✗ FFmpeg test failed")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("FFmpeg Installer for YouTube Downloader")
    print("=" * 50)

    # Check if FFmpeg already exists
    if os.path.exists("ffmpeg.exe"):
        print("FFmpeg already exists in current directory")
        test = input("Test existing FFmpeg? (y/n): ").strip().lower()
        if test == "y":
            result = subprocess.run(
                ["ffmpeg.exe", "-version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✓ FFmpeg is working!")
                version_line = result.stdout.split("\n")[0]
                print(f"Version: {version_line}")
            else:
                print("✗ FFmpeg is not working")
                reinstall = input("Download new version? (y/n): ").strip().lower()
                if reinstall == "y":
                    download_ffmpeg()
    else:
        print("FFmpeg not found")
        install = input("Download FFmpeg? (y/n): ").strip().lower()
        if install == "y":
            if download_ffmpeg():
                print("\n" + "=" * 50)
                print("✓ FFmpeg successfully installed!")
                print("Now you can download YouTube videos in best quality")
            else:
                print("\n" + "=" * 50)
                print("✗ FFmpeg installation failed")
                print("\nManual installation:")
                print("1. Download from: https://ffmpeg.org/download.html")
                print("2. Extract ffmpeg.exe to this folder")
                print("3. Or add FFmpeg to your system PATH")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
