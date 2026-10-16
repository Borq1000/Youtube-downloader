#!/usr/bin/env python3
"""
Test FFmpeg in EXE - Verify video+audio download works
This script tests if FFmpeg is correctly bundled and working
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def test_ffmpeg_binary():
    """Test if FFmpeg binary is accessible"""
    print("\n" + "=" * 60)
    print("TESTING FFMPEG BINARY ACCESS")
    print("=" * 60)

    # Check if running as EXE
    if getattr(sys, "frozen", False):
        print(f"✓ Running as EXE from: {sys._MEIPASS}")

        # Check for FFmpeg in bundle
        ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        ffprobe_path = os.path.join(sys._MEIPASS, "ffprobe.exe")

        if os.path.exists(ffmpeg_path):
            print(f"✓ FFmpeg found: {ffmpeg_path}")
            # Test FFmpeg execution
            try:
                result = subprocess.run(
                    [ffmpeg_path, "-version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    print("✓ FFmpeg executes successfully!")
                else:
                    print(f"✗ FFmpeg failed: {result.stderr}")
            except Exception as e:
                print(f"✗ Cannot run FFmpeg: {e}")
        else:
            print("✗ FFmpeg NOT found in bundle!")

        if os.path.exists(ffprobe_path):
            print(f"✓ FFprobe found: {ffprobe_path}")
        else:
            print("✗ FFprobe NOT found in bundle!")
    else:
        print("Running as script (not EXE)")
        if os.path.exists("ffmpeg.exe"):
            print("✓ FFmpeg found in current directory")
        else:
            print("✗ FFmpeg not found")


def test_youtube_download():
    """Test actual YouTube download with format selection"""
    print("\n" + "=" * 60)
    print("TESTING YOUTUBE DOWNLOAD")
    print("=" * 60)

    try:
        import yt_dlp
    except ImportError:
        print("✗ yt-dlp not available")
        return False

    # Test video URL (short public video)
    test_url = "https://www.youtube.com/watch?v=BaW_jenozKc"  # YouTube test video

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test_video.mp4")

        ydl_opts = {
            "outtmpl": output_file,
            "quiet": False,
            "no_warnings": False,
        }

        # Setup FFmpeg location if in EXE
        if getattr(sys, "frozen", False):
            ffmpeg_dir = sys._MEIPASS
            ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

            if os.path.exists(ffmpeg_path):
                ydl_opts["ffmpeg_location"] = ffmpeg_dir
                print(f"Using FFmpeg from: {ffmpeg_dir}")
            else:
                print("WARNING: FFmpeg not found in bundle!")

        # Test 1: Try to get video+audio format
        print("\nTest 1: Downloading with best video+audio...")
        ydl_opts["format"] = "best[ext=mp4]/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)

                # Check available formats
                formats = info.get("formats", [])
                has_video_audio = False

                for fmt in formats:
                    has_video = fmt.get("vcodec", "none") != "none"
                    has_audio = fmt.get("acodec", "none") != "none"
                    if has_video and has_audio:
                        has_video_audio = True
                        print(
                            f"✓ Found format {fmt['format_id']}: {fmt.get('format_note', '')} (video+audio)"
                        )
                        break

                if not has_video_audio:
                    print("✗ No combined video+audio formats found")
                    print("FFmpeg is required to merge separate streams!")

                # Try actual download
                print("\nAttempting download...")
                result = ydl.extract_info(test_url, download=True)

                if os.path.exists(output_file):
                    size_mb = os.path.getsize(output_file) / (1024 * 1024)
                    print(f"✓ Downloaded: {size_mb:.2f} MB")

                    # Check if file has video stream
                    if check_video_stream(output_file):
                        print("✓ Video stream detected!")
                        return True
                    else:
                        print("✗ No video stream - audio only!")
                        return False
                else:
                    print("✗ Download failed - no output file")
                    return False

        except Exception as e:
            print(f"✗ Download error: {e}")
            return False


def check_video_stream(file_path):
    """Check if file contains video stream using ffprobe"""
    if getattr(sys, "frozen", False):
        ffprobe_path = os.path.join(sys._MEIPASS, "ffprobe.exe")
    else:
        ffprobe_path = "ffprobe.exe"

    if not os.path.exists(ffprobe_path):
        print("Cannot verify video stream (ffprobe not found)")
        return None

    try:
        result = subprocess.run(
            [
                ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_type",
                "-of",
                "csv=p=0",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        has_video = "video" in result.stdout
        return has_video
    except:
        return None


def main():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║           FFmpeg EXE Integration Test                   ║
║              Testing Video Download                     ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    # Test 1: Binary access
    test_ffmpeg_binary()

    # Test 2: YouTube download
    success = test_youtube_download()

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    if success:
        print("✅ SUCCESS: Video download works with FFmpeg!")
        print("The EXE should be able to download videos with both audio and video.")
    else:
        print("❌ FAILURE: FFmpeg integration not working!")
        print("The EXE will only download audio without video.")
        print("\nPossible solutions:")
        print("1. Ensure ffmpeg.exe and ffprobe.exe are in the same folder")
        print("2. Rebuild EXE with create_exe_with_ffmpeg.py")
        print("3. Use youtube_downloader_fixed.py which uses pre-merged formats")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
