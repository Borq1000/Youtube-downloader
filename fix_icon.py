#!/usr/bin/env python3
"""
Fix icon.ico file for YouTube Downloader Pro
"""

import os
import sys


def remove_bad_icon():
    """Remove corrupted icon file"""
    if os.path.exists("icon.ico"):
        os.remove("icon.ico")
        print("✅ Removed corrupted icon.ico")


def create_default_icon():
    """Create a default icon using Pillow"""
    try:
        from PIL import Image, ImageDraw

        print("Creating new icon.ico...")

        # Create a simple icon
        size = 256
        img = Image.new("RGBA", (size, size), (45, 45, 45, 255))
        draw = ImageDraw.Draw(img)

        # Draw YouTube-style play button
        # Red background circle
        draw.ellipse([20, 20, size - 20, size - 20], fill=(255, 0, 0, 255))

        # White play triangle
        points = [
            (size * 0.4, size * 0.35),  # left point
            (size * 0.4, size * 0.65),  # bottom left
            (size * 0.65, size * 0.5),  # right point
        ]
        draw.polygon(points, fill=(255, 255, 255, 255))

        # Save as PNG first
        img.save("icon.png", "PNG")
        print("✅ Created icon.png")

        # Create ICO with multiple sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []

        for s in sizes:
            resized = img.resize(s, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO
        img.save("icon.ico", format="ICO", sizes=sizes)
        print("✅ Created new icon.ico with all sizes")

        return True

    except ImportError:
        print("❌ Pillow not installed.")
        print("Installing Pillow...")
        os.system(f"{sys.executable} -m pip install pillow")
        return create_default_icon()
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False


def build_without_icon():
    """Modify create_exe.py to build without icon"""
    print("\nModifying build script to work without icon...")

    # Read the create_exe.py file
    with open("create_exe.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Remove icon parameter
    content = content.replace(
        '# Add icon if exists\n        "--icon", "icon.ico" if os.path.exists("icon.ico") else "",',
        '# Icon disabled due to error\n        # "--icon", "icon.ico",',
    )

    # Save modified version
    with open("create_exe_no_icon.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Created create_exe_no_icon.py (builds without icon)")


def main():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║              Icon Fix Tool for EXE Builder              ║
║                Created by Божидар Алемков               ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    print("The icon.ico file is corrupted or invalid.")
    print("\nSelect solution:")
    print("1. Create new default icon (recommended)")
    print("2. Build EXE without icon")
    print("3. Exit and add icon manually")

    choice = input("\nChoice (1-3): ").strip()

    if choice == "1":
        # Remove bad icon
        remove_bad_icon()

        # Create new icon
        if create_default_icon():
            print("\n✅ Icon fixed successfully!")
            print("\nNow run: python create_exe.py")
        else:
            print("\n❌ Could not create icon")
            build_without_icon()
            print("\nRun: python create_exe_no_icon.py")

    elif choice == "2":
        build_without_icon()
        print("\nRun: python create_exe_no_icon.py")
        print("(This will create EXE without custom icon)")

    else:
        print("\nTo add icon manually:")
        print("1. Delete current icon.ico")
        print("2. Go to https://convertico.com/")
        print("3. Upload your image (PNG/JPG)")
        print("4. Download as icon.ico")
        print("5. Run: python create_exe.py")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
