#!/usr/bin/env python3
"""
Download and setup FFmpeg for the application
This will be included when creating .exe
"""

import os
import sys
import zipfile
import urllib.request
import shutil


def download_ffmpeg():
    """Download FFmpeg binaries for Windows"""
    print("Setting up FFmpeg for YouTube Downloader...")
    print("=" * 60)

    # Check if already exists
    if os.path.exists("ffmpeg.exe") and os.path.exists("ffprobe.exe"):
        print("✅ FFmpeg already installed in app folder")
        return True

    # FFmpeg download URL
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg_temp.zip"

    try:
        # Download FFmpeg
        print(f"Downloading FFmpeg...")
        print("This may take a few minutes...")

        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            print(f"Progress: {percent:.1f}%", end="\r")

        urllib.request.urlretrieve(url, zip_path, download_progress)
        print("\n✓ Download complete")

        # Extract FFmpeg
        print("\nExtracting FFmpeg...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Extract to temp folder
            zip_ref.extractall("ffmpeg_temp")
        print("✓ Extraction complete")

        # Find the extracted folder
        extracted_folder = None
        for item in os.listdir("ffmpeg_temp"):
            if item.startswith("ffmpeg-") and os.path.isdir(
                os.path.join("ffmpeg_temp", item)
            ):
                extracted_folder = os.path.join("ffmpeg_temp", item)
                break

        if not extracted_folder:
            print("✗ Could not find extracted FFmpeg folder")
            return False

        # Copy FFmpeg executables to current directory
        bin_path = os.path.join(extracted_folder, "bin")
        if os.path.exists(bin_path):
            files_to_copy = ["ffmpeg.exe", "ffprobe.exe"]
            for exe in files_to_copy:
                src = os.path.join(bin_path, exe)
                dst = exe
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"✓ Copied {exe}")

        # Clean up
        print("\nCleaning up...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("ffmpeg_temp"):
            shutil.rmtree("ffmpeg_temp")
        print("✓ Cleanup complete")

        # Verify installation
        if os.path.exists("ffmpeg.exe") and os.path.exists("ffprobe.exe"):
            print("\n" + "=" * 60)
            print("✅ FFmpeg successfully installed!")
            print("Location: App folder (will be included in .exe)")
            return True
        else:
            print("\n✗ FFmpeg installation failed")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")

        # Clean up on error
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("ffmpeg_temp"):
            shutil.rmtree("ffmpeg_temp")

        print("\nManual installation:")
        print("1. Download from: https://ffmpeg.org/download.html")
        print("2. Extract ffmpeg.exe and ffprobe.exe to app folder")

        return False


if __name__ == "__main__":
    success = download_ffmpeg()
    if success:
        print("\nFFmpeg is ready!")
        print("The application will now use FFmpeg for best quality downloads")
    else:
        print("\nFFmpeg setup failed")
        print("The application will still work but with limited quality")

    input("\nPress Enter to exit...")
