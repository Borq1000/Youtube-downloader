#!/usr/bin/env python3
"""
Simple downloader using Edge browser (usually works better than Chrome)
"""

import yt_dlp
import os


def download_video():
    print("YouTube Downloader (Using Edge Browser)")
    print("=" * 50)
    print("Make sure you're logged into YouTube in Microsoft Edge")
    print()

    url = input("Enter YouTube URL: ").strip()

    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiesfrombrowser": ("edge", None),
        "format": "best[ext=mp4]/best",
    }

    # Create downloads folder
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    print("\nDownloading using Edge browser cookies...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown")
            print(f"\n✅ Successfully downloaded: {title}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

        if "could not copy" in str(e).lower():
            print("\nTry these solutions:")
            print("1. Close Microsoft Edge completely")
            print("2. Try using Firefox instead")
            print("3. Run: python fix_chrome_cookies.py")


if __name__ == "__main__":
    download_video()
    input("\nPress Enter to exit...")
