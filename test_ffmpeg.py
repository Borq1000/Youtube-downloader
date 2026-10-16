#!/usr/bin/env python3
"""
Test FFmpeg detection
"""

import os
import subprocess

print("FFmpeg Detection Test")
print("=" * 50)

# Current directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")
print()

# List all .exe files
print("EXE files in current directory:")
for file in os.listdir(current_dir):
    if file.endswith(".exe"):
        size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
        print(f"  - {file} ({size:.1f} MB)")
print()

# Test FFmpeg
ffmpeg_found = False
ffmpeg_path = None

# Check different paths
paths_to_check = [
    "ffmpeg.exe",
    os.path.join(current_dir, "ffmpeg.exe"),
    os.path.abspath("ffmpeg.exe"),
]

print("Checking FFmpeg paths:")
for path in paths_to_check:
    exists = os.path.exists(path)
    is_file = os.path.isfile(path) if exists else False
    print(f"  {path}")
    print(f"    Exists: {exists}, Is file: {is_file}")

    if exists and is_file:
        try:
            result = subprocess.run(
                [path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
            if result.returncode == 0:
                ffmpeg_found = True
                ffmpeg_path = path
                print(f"    ✅ WORKS! FFmpeg version detected")
                # Get version info
                output = result.stdout.decode("utf-8", errors="ignore")
                first_line = output.split("\n")[0] if output else ""
                print(f"    Version: {first_line}")
                break
            else:
                print(
                    f"    ❌ File exists but execution failed (return code: {result.returncode})"
                )
        except Exception as e:
            print(f"    ❌ Error running: {e}")

print()

# Also check system PATH
if not ffmpeg_found:
    print("Checking system PATH:")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if result.returncode == 0:
            ffmpeg_found = True
            print("  ✅ FFmpeg found in system PATH")
        else:
            print("  ❌ Not found in system PATH")
    except FileNotFoundError:
        print("  ❌ FFmpeg not in system PATH")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("=" * 50)
if ffmpeg_found:
    print("✅ RESULT: FFmpeg is working!")
    if ffmpeg_path:
        print(f"   Location: {ffmpeg_path}")
else:
    print("❌ RESULT: FFmpeg not found or not working")
    print("\nTo fix this:")
    print("1. Run: python setup_ffmpeg.py")
    print("2. Or download manually from: https://ffmpeg.org/download.html")
    print("3. Place ffmpeg.exe in this folder")

input("\nPress Enter to exit...")
