#!/usr/bin/env python3
"""
Prepare and verify icons for YouTube Downloader Pro
"""

import os
from PIL import Image
import requests
import io


def check_icons():
    """Check if icons are ready"""
    print("Icon Preparation Tool")
    print("=" * 60)

    icons_status = {"icon.ico": False, "icon.png": False}

    # Check ICO file
    if os.path.exists("icon.ico"):
        size = os.path.getsize("icon.ico") / 1024
        print(f"✅ icon.ico found ({size:.1f} KB)")
        icons_status["icon.ico"] = True
    else:
        print("❌ icon.ico not found")

    # Check PNG file
    if os.path.exists("icon.png"):
        try:
            img = Image.open("icon.png")
            print(f"✅ icon.png found ({img.size[0]}x{img.size[1]} px)")
            icons_status["icon.png"] = True
        except:
            print("❌ icon.png found but cannot be opened")
    else:
        print("❌ icon.png not found")

    return all(icons_status.values())


def create_sample_icon():
    """Create a sample icon if none exists"""
    print("\nCreating sample icon...")

    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a simple icon with "YT"
        size = 256
        img = Image.new("RGBA", (size, size), (30, 30, 30, 255))
        draw = ImageDraw.Draw(img)

        # Draw background gradient effect
        for i in range(size // 2):
            alpha = 255 - (i * 2)
            color = (0, 122, 204, alpha)  # Blue gradient
            draw.rectangle([i, i, size - i, size - i], outline=color)

        # Draw "YT" text
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", size // 3)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        text = "YT"
        draw.text((size // 4, size // 3), text, fill=(255, 255, 255), font=font)

        # Save as PNG
        img.save("icon.png", "PNG")
        print("✅ Created icon.png")

        # Create ICO with multiple sizes
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []

        for icon_size in icon_sizes:
            resized = img.resize(icon_size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO
        icons[0].save(
            "icon.ico", format="ICO", sizes=icon_sizes, append_images=icons[1:]
        )
        print("✅ Created icon.ico with multiple sizes")

        return True

    except ImportError:
        print("❌ Pillow not installed. Cannot create sample icons.")
        print("   Install with: pip install pillow")
        return False
    except Exception as e:
        print(f"❌ Error creating icons: {e}")
        return False


def main():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║           YouTube Downloader Pro - Icon Setup           ║
║                 Created by Божидар Алемков              ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    # Check existing icons
    if check_icons():
        print("\n✅ All icons are ready!")
        print("\nYour icons will be used for:")
        print("  • Window icon (top-left corner)")
        print("  • EXE file icon")
        print("  • Desktop shortcut icon")
    else:
        print("\n" + "=" * 60)
        print("INSTRUCTIONS FOR CREATING ICONS:")
        print("=" * 60)

        print(
            """
1. PREPARE YOUR IMAGE:
   • Square image (1:1 ratio)
   • At least 256x256 px (512x512 is better)
   • PNG format with transparent background (optional)

2. CONVERT TO ICO:
   • Go to: https://convertico.com/
   • Upload your image
   • Download as 'icon.ico'
   • Save to this folder

3. OPTIONAL - CREATE PNG VERSION:
   • Resize your image to 64x64 px
   • Save as 'icon.png' in this folder

4. RECOMMENDED ONLINE TOOLS:
   • ConvertICO.com - Best for multi-size ICO
   • ICOConvert.com - More size options
   • Favicon.io - Simple and fast
        """
        )

        # Offer to create sample icon
        response = input("\nCreate sample icon? (y/n): ").lower()
        if response == "y":
            if create_sample_icon():
                print("\n✅ Sample icons created!")
                print("You can replace them with your own icons later.")
            else:
                print("\n❌ Could not create sample icons")

    print("\n" + "=" * 60)
    print("After adding your icons, run: python create_exe.py")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
