#!/usr/bin/env python3
"""
Get fresh cookies directly from browser
"""

import subprocess
import sys

print("Getting fresh cookies from your browser...")
print("=" * 50)

browsers = {"1": "chrome", "2": "firefox", "3": "edge", "4": "brave", "5": "opera"}

print("Select your browser:")
for key, browser in browsers.items():
    print(f"{key}. {browser.capitalize()}")

choice = input("\nEnter number (1-5): ").strip()

if choice not in browsers:
    print("Invalid choice")
    sys.exit(1)

browser = browsers[choice]

print(f"\nExtracting cookies from {browser.capitalize()}...")
print("Make sure you are logged into YouTube in your {browser.capitalize()} browser!")
print("-" * 50)

# Extract cookies using yt-dlp
cmd = [
    "yt-dlp",
    "--cookies-from-browser",
    browser,
    "--cookies",
    "cookies.txt",
    "--skip-download",
    "https://www.youtube.com",
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True)

    if (
        "browser cookies extracted successfully" in result.stderr.lower()
        or result.returncode == 0
    ):
        print("\n✓ Cookies successfully extracted and saved to cookies.txt")
        print("\nNow you can run the downloader!")
    else:
        print("\n✗ Failed to extract cookies")
        print("Error:", result.stderr if result.stderr else result.stdout)
        print("\nTroubleshooting:")
        print("1. Make sure your browser is closed")
        print("2. Make sure you're logged into YouTube in that browser")
        print("3. Try a different browser")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nAlternative method - run this command manually:")
    print(
        f"yt-dlp --cookies-from-browser {browser} --cookies cookies.txt --skip-download https://www.youtube.com"
    )

input("\nPress Enter to exit...")
