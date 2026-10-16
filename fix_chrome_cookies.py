#!/usr/bin/env python3
"""
Fix Chrome cookie database access issues
"""

import os
import sys
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path


def find_chrome_cookies():
    """Find Chrome cookies database location"""
    possible_paths = [
        # Windows paths
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/User Data/Default/Network/Cookies",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/User Data/Default/Cookies",
        Path(os.environ.get("APPDATA", ""))
        / "../Local/Google/Chrome/User Data/Default/Network/Cookies",
        Path(os.environ.get("APPDATA", ""))
        / "../Local/Google/Chrome/User Data/Default/Cookies",
    ]

    for path in possible_paths:
        if path.exists():
            return path
    return None


def solution_1_close_chrome():
    """Solution 1: Close Chrome and retry"""
    print("=" * 60)
    print("SOLUTION 1: Close Chrome completely")
    print("=" * 60)
    print("\nChrome locks the cookie database while running.")
    print("\nSteps:")
    print("1. Close ALL Chrome windows")
    print("2. Open Task Manager (Ctrl+Shift+Esc)")
    print("3. End all 'chrome.exe' processes")
    print("4. Try downloading again")

    input("\nPress Enter after closing Chrome...")

    # Check if Chrome is still running
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True,
        )
        if "chrome.exe" in result.stdout:
            print("⚠️ Chrome is still running!")
            kill = input("Kill all Chrome processes? (y/n): ").lower()
            if kill == "y":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True
                )
                print("✅ Chrome processes killed")
        else:
            print("✅ Chrome is not running")
    except:
        pass


def solution_2_copy_cookies():
    """Solution 2: Copy cookies database to temp location"""
    print("\n" + "=" * 60)
    print("SOLUTION 2: Copy cookies database")
    print("=" * 60)

    cookies_path = find_chrome_cookies()
    if not cookies_path:
        print("❌ Could not find Chrome cookies database")
        return False

    print(f"Found cookies at: {cookies_path}")

    # Create a temporary copy
    temp_dir = tempfile.mkdtemp()
    temp_cookies = Path(temp_dir) / "Cookies"

    try:
        shutil.copy2(cookies_path, temp_cookies)
        print(f"✅ Copied cookies to: {temp_cookies}")

        # Set environment variable for yt-dlp
        os.environ["YT_DLP_CHROME_COOKIES_FILE"] = str(temp_cookies)
        print("\n✅ Set temporary cookies path for yt-dlp")

        return True
    except Exception as e:
        print(f"❌ Failed to copy: {e}")
        return False


def solution_3_use_different_browser():
    """Solution 3: Use a different browser"""
    print("\n" + "=" * 60)
    print("SOLUTION 3: Use a different browser")
    print("=" * 60)
    print("\nTry using Firefox or Edge instead:")
    print("\n1. Make sure you're logged into YouTube in Firefox/Edge")
    print("2. Use 'firefox' or 'edge' in the browser dropdown")
    print("\nFirefox usually has fewer cookie access issues than Chrome")


def solution_4_manual_export():
    """Solution 4: Manual cookie export using browser extension"""
    print("\n" + "=" * 60)
    print("SOLUTION 4: Export cookies manually")
    print("=" * 60)
    print("\n1. Install browser extension:")
    print("   • Chrome: 'Get cookies.txt LOCALLY'")
    print("   • Firefox: 'cookies.txt'")
    print("\n2. Go to YouTube and make sure you're logged in")
    print("\n3. Click the extension icon")
    print("\n4. Save cookies.txt to this folder")
    print("\n5. The program will use the cookies.txt file instead")


def solution_5_alternative_download():
    """Solution 5: Use alternative download method"""
    print("\n" + "=" * 60)
    print("SOLUTION 5: Alternative download command")
    print("=" * 60)
    print("\nTry this command directly in terminal:")
    print("\n1. First, close Chrome completely")
    print("\n2. Then run:")
    print(
        "   yt-dlp --cookies-from-browser chrome:C:/path/to/profile https://youtu.be/VIDEO_ID"
    )
    print("\nOr with Edge (usually works better):")
    print("   yt-dlp --cookies-from-browser edge https://youtu.be/VIDEO_ID")


def main():
    print("🔧 Chrome Cookie Database Fix Tool")
    print("=" * 60)

    while True:
        print("\nSelect a solution to try:")
        print("1. Close Chrome and retry")
        print("2. Copy cookies database (automatic)")
        print("3. Use different browser (Firefox/Edge)")
        print("4. Export cookies manually")
        print("5. Alternative download method")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            solution_1_close_chrome()
        elif choice == "2":
            solution_2_copy_cookies()
        elif choice == "3":
            solution_3_use_different_browser()
        elif choice == "4":
            solution_4_manual_export()
        elif choice == "5":
            solution_5_alternative_download()
        elif choice == "6":
            break
        else:
            print("Invalid choice")

    print("\n✅ After applying the fix, try downloading again")
    print("   Run: python youtube_gui_simple.py")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
