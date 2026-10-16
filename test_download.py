#!/usr/bin/env python3
"""
Test script to download a YouTube video with detailed debugging
"""

import yt_dlp
import os


def test_download():
    url = input("Enter YouTube URL to test: ").strip()

    # First try to get cookies from browser
    browser_choice = input("\nGet fresh cookies from browser? (y/n): ").strip().lower()

    if browser_choice == "y":
        browsers = ["chrome", "firefox", "edge", "brave", "opera"]
        print("\nAvailable browsers:")
        for i, browser in enumerate(browsers, 1):
            print(f"{i}. {browser.capitalize()}")

        choice = input("Select browser (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 5:
            browser = browsers[int(choice) - 1]
            print(f"\nGetting cookies from {browser}...")

            ydl_opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "restrictfilenames": True,
                "windowsfilenames": True,
                "nocheckcertificate": True,
                "cookiesfrombrowser": (browser, None),
                "verbose": True,
            }
    else:
        ydl_opts = {
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "restrictfilenames": True,
            "windowsfilenames": True,
            "nocheckcertificate": True,
            "verbose": True,  # Enable verbose output for debugging
        }

        # Add cookies if available
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"
            print("Using cookies.txt for authentication")

    print("\nOptions being used:")
    for key, value in ydl_opts.items():
        if key != "verbose":
            print(f"  {key}: {value}")

    print("\nStarting download...")
    print("-" * 50)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"\nVideo Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 0)} seconds")
            print(f"Uploader: {info.get('uploader', 'Unknown')}")

            print("\nAvailable formats:")
            formats = info.get("formats", [])
            for f in formats[:10]:  # Show first 10 formats
                print(
                    f"  Format {f.get('format_id')}: {f.get('format_note')} - {f.get('ext')}"
                )

            print("\nDownloading...")
            ydl.download([url])
            print("\n✓ Download completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTrying alternative method...")

        # Try with simpler options
        simple_opts = {
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "format": "best",
        }

        if os.path.exists("cookies.txt"):
            simple_opts["cookiefile"] = "cookies.txt"

        try:
            with yt_dlp.YoutubeDL(simple_opts) as ydl:
                ydl.download([url])
                print("\n✓ Download completed with simple options!")
        except Exception as e2:
            print(f"\n✗ Alternative method also failed: {str(e2)}")


if __name__ == "__main__":
    test_download()
    input("\nPress Enter to exit...")
