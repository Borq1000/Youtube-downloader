#!/usr/bin/env python3
"""
Create standalone EXE for YouTube Downloader Pro
Created by Божидар Алемков
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime


def create_exe():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║         YouTube Downloader Pro - EXE Builder            ║
║              Created by Божидар Алемков                 ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    # Check if main script exists
    if not os.path.exists("youtube_downloader_final.py"):
        print("❌ youtube_downloader_final.py not found!")
        return False

    # Check for FFmpeg
    if not os.path.exists("ffmpeg.exe"):
        print("⚠️ FFmpeg not found. Downloading...")
        subprocess.run([sys.executable, "setup_ffmpeg.py"])

    print("Building YouTube Downloader Pro.exe...")
    print("=" * 60)

    # PyInstaller command with all options
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Single exe file
        "--windowed",  # No console window
        "--name",
        "YouTube_Downloader_Pro",
        "--distpath",
        "dist",
        "--workpath",
        "build",
        "--specpath",
        ".",
        # Add icon if exists
        "--icon",
        "icon.ico" if os.path.exists("icon.ico") else "",
        # Add FFmpeg files
        "--add-binary",
        "ffmpeg.exe;.",
        "--add-binary",
        "ffprobe.exe;.",
        # Add icon files as data
        "--add-data",
        "icon.ico;." if os.path.exists("icon.ico") else "",
        "--add-data",
        "icon.png;." if os.path.exists("icon.png") else "",
        # Add data files if they exist
        "--add-data",
        "cookies.txt;." if os.path.exists("cookies.txt") else "",
        # Hidden imports for all dependencies
        "--hidden-import",
        "yt_dlp",
        "--hidden-import",
        "yt_dlp.extractor",
        "--hidden-import",
        "yt_dlp.downloader",
        "--hidden-import",
        "yt_dlp.postprocessor",
        "--hidden-import",
        "PyQt6",
        "--hidden-import",
        "PyQt6.QtCore",
        "--hidden-import",
        "PyQt6.QtGui",
        "--hidden-import",
        "PyQt6.QtWidgets",
        # Optimization
        "--optimize",
        "2",
        # Clean build
        "--clean",
        # Main script
        "youtube_downloader_final.py",
    ]

    # Remove empty arguments
    cmd = [arg for arg in cmd if arg]

    print("Running PyInstaller...")
    print("This may take 2-5 minutes...\n")

    try:
        result = subprocess.run(cmd, text=True)

        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ BUILD SUCCESSFUL!")
            print("=" * 60)

            # Get file size
            exe_path = "dist/YouTube_Downloader_Pro.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"\nExecutable: {exe_path}")
                print(f"Size: {size_mb:.1f} MB")

                # Create distribution package
                create_distribution_package()

                return True
            else:
                print("❌ EXE file not found after build")
                return False
        else:
            print("\n❌ Build failed!")
            return False

    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False


def create_distribution_package():
    """Create a distribution folder with all necessary files"""
    print("\nCreating distribution package...")

    dist_folder = f"YouTube_Downloader_Pro_{datetime.now().strftime('%Y%m%d')}"

    # Remove old distribution folder if exists
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)

    os.makedirs(dist_folder)

    # Copy exe
    shutil.copy2("dist/YouTube_Downloader_Pro.exe", dist_folder)

    # Create README
    readme_content = """
YouTube Downloader Pro
═══════════════════════════════════════════════════════════════

Created by: Божидар Алемков

FEATURES:
• Download YouTube videos in best quality
• Extract audio to MP3
• Multi-language support (English/Русский)
• Built-in FFmpeg for maximum quality
• Simple and intuitive interface

HOW TO USE:
1. Run YouTube_Downloader_Pro.exe
2. Get cookies from YouTube:
   - Install Chrome extension "Get cookies.txt LOCALLY"
   - Go to YouTube and log in
   - Click extension icon → Export
   - Copy all text
3. Paste cookies in Settings tab
4. Enter YouTube URL
5. Click Download

SYSTEM REQUIREMENTS:
• Windows 10 or later
• Internet connection
• 200 MB free disk space

TROUBLESHOOTING:
• If videos don't download: Update cookies
• If quality is limited: FFmpeg is already included
• For help: Check Settings tab for instructions

═══════════════════════════════════════════════════════════════
Version 1.0 | 2024
"""

    with open(f"{dist_folder}/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Create quick start guide in Russian
    readme_ru = """
YouTube Загрузчик Pro
═══════════════════════════════════════════════════════════════

Создатель: Божидар Алемков

ВОЗМОЖНОСТИ:
• Скачивание видео с YouTube в лучшем качестве
• Извлечение аудио в MP3
• Поддержка русского языка
• Встроенный FFmpeg для максимального качества
• Простой и понятный интерфейс

КАК ИСПОЛЬЗОВАТЬ:
1. Запустите YouTube_Downloader_Pro.exe
2. Получите cookies с YouTube:
   - Установите расширение Chrome "Get cookies.txt LOCALLY"
   - Зайдите на YouTube и войдите в аккаунт
   - Нажмите на иконку расширения → Export
   - Скопируйте весь текст
3. Вставьте cookies во вкладке Настройки
4. Введите URL видео
5. Нажмите Скачать

СИСТЕМНЫЕ ТРЕБОВАНИЯ:
• Windows 10 или новее
• Подключение к интернету
• 200 МБ свободного места

РЕШЕНИЕ ПРОБЛЕМ:
• Если видео не скачивается: Обновите cookies
• Если качество ограничено: FFmpeg уже включен
• Для помощи: Смотрите инструкции во вкладке Настройки

═══════════════════════════════════════════════════════════════
Версия 1.0 | 2024
"""

    with open(f"{dist_folder}/README_RU.txt", "w", encoding="utf-8") as f:
        f.write(readme_ru)

    print(f"✅ Distribution package created: {dist_folder}/")
    print(f"   • YouTube_Downloader_Pro.exe")
    print(f"   • README.txt")
    print(f"   • README_RU.txt")


def cleanup():
    """Clean up build files"""
    print("\nCleaning up build files...")

    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["YouTube_Downloader_Pro.spec"]

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   Removed {file_name}")

    print("✅ Cleanup complete")


def main():
    # Create exe
    if create_exe():
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Your application is ready!")
        print("=" * 60)
        print("\nThe EXE file includes:")
        print("  • All Python dependencies")
        print("  • FFmpeg for best quality")
        print("  • PyQt6 interface")
        print("  • yt-dlp downloader")
        print("\nYou can now distribute the YouTube_Downloader_Pro.exe file")
        print("It will work on any Windows 10+ computer")

        # Ask about cleanup
        response = input("\nClean up build files? (y/n): ").lower()
        if response == "y":
            cleanup()
    else:
        print("\n❌ Build failed. Check error messages above.")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
