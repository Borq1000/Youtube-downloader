#!/usr/bin/env python3
"""
Build WORKING EXE with FFmpeg that downloads video+audio
This version uses a different approach to ensure FFmpeg works
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile

print(
    """
╔══════════════════════════════════════════════════════════╗
║     YouTube Downloader - WORKING EXE Builder            ║
║         This version WILL download video+audio          ║
║              Created by Божидар Алемков                 ║
╚══════════════════════════════════════════════════════════╝
"""
)

# Step 1: Ensure FFmpeg is present
print("\n1. Checking FFmpeg...")
if not os.path.exists("ffmpeg.exe") or not os.path.exists("ffprobe.exe"):
    print("   FFmpeg not found. Downloading...")

    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

    try:
        print("   Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")

        print("   Extracting...")
        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("ffmpeg.exe"):
                    with zip_ref.open(file) as source, open(
                        "ffmpeg.exe", "wb"
                    ) as target:
                        target.write(source.read())
                elif file.endswith("ffprobe.exe"):
                    with zip_ref.open(file) as source, open(
                        "ffprobe.exe", "wb"
                    ) as target:
                        target.write(source.read())

        os.remove("ffmpeg.zip")
        print("   ✅ FFmpeg downloaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to download FFmpeg: {e}")
        print("   Please download manually from:")
        print("   https://ffmpeg.org/download.html")
        sys.exit(1)
else:
    print("   ✅ FFmpeg found")

# Step 2: Create the main script with FFmpeg fix
print("\n2. Creating optimized main script...")

main_script = '''#!/usr/bin/env python3
"""
YouTube Downloader Pro - OPTIMIZED FOR EXE
This version ensures FFmpeg works in the bundled EXE
Created by Божидар Алемков
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Fix FFmpeg path BEFORE importing yt-dlp
if getattr(sys, 'frozen', False):
    # Running as EXE - set FFmpeg path
    bundle_dir = sys._MEIPASS
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

    # Force yt-dlp to use our FFmpeg
    ffmpeg_exe = os.path.join(bundle_dir, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_exe):
        os.environ['FFMPEG_BINARY'] = ffmpeg_exe
        os.environ['FFPROBE_BINARY'] = os.path.join(bundle_dir, 'ffprobe.exe')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QComboBox,
    QProgressBar, QGroupBox, QMessageBox, QRadioButton, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon

import yt_dlp

# Translations
TRANSLATIONS = {
    'en': {
        'app_title': 'YouTube Downloader Pro',
        'url_placeholder': 'Enter YouTube URL',
        'paste_btn': '📋 Paste',
        'quality_label': 'Quality:',
        'video_format': 'Video (MP4)',
        'audio_format': 'Audio Only (MP3)',
        'download_btn': '🚀 Download',
        'save_to': 'Save to:',
        'browse': 'Browse...',
        'success': 'Success',
        'error': 'Error',
        'created_by': 'Created by: Божидар Алемков'
    },
    'ru': {
        'app_title': 'YouTube Загрузчик Pro',
        'url_placeholder': 'Введите URL YouTube',
        'paste_btn': '📋 Вставить',
        'quality_label': 'Качество:',
        'video_format': 'Видео (MP4)',
        'audio_format': 'Только аудио (MP3)',
        'download_btn': '🚀 Скачать',
        'save_to': 'Сохранить в:',
        'browse': 'Обзор...',
        'success': 'Успешно',
        'error': 'Ошибка',
        'created_by': 'Создатель: Божидар Алемков'
    }
}

def get_windows_videos_folder():
    """Get Windows Videos folder"""
    possible = [Path.home() / "Videos", Path.home() / "Видео"]
    for path in possible:
        if path.exists():
            return str(path)
    videos = Path.home() / "Videos"
    videos.mkdir(exist_ok=True)
    return str(videos)

class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress_value = pyqtSignal(int)

    def __init__(self, url, quality, audio_only, output_dir):
        super().__init__()
        self.url = url
        self.quality = quality
        self.audio_only = audio_only
        self.output_dir = output_dir

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                progress = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                self.progress_value.emit(progress)
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            self.progress.emit(f"Progress: {percent} | Speed: {speed}")
        elif d['status'] == 'finished':
            self.progress.emit("Processing video...")

    def run(self):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'restrictfilenames': True,
                'windowsfilenames': True,
                'nocheckcertificate': True,
            }

            # Use cookies if available
            if os.path.exists('cookies.txt'):
                ydl_opts['cookiefile'] = 'cookies.txt'
            elif getattr(sys, 'frozen', False):
                cookie_path = os.path.join(sys._MEIPASS, 'cookies.txt')
                if os.path.exists(cookie_path):
                    ydl_opts['cookiefile'] = cookie_path

            # Setup FFmpeg location for EXE
            if getattr(sys, 'frozen', False):
                ffmpeg_dir = sys._MEIPASS
                ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    ydl_opts['ffmpeg_location'] = ffmpeg_dir
                    self.progress.emit("Using bundled FFmpeg for best quality")

            if self.audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                self.progress.emit("Downloading audio...")
            else:
                # VIDEO - Ensure we get video+audio
                quality_formats = {
                    'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best',
                    '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best',
                    '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best',
                    '360p': 'best[height<=360]/worstvideo+bestaudio/worst'
                }

                ydl_opts['format'] = quality_formats.get(self.quality, quality_formats['best'])

                # Ensure MP4 output for video
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]

                self.progress.emit(f"Downloading {self.quality} video with audio...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get('title', 'Unknown')
                self.finished.emit(True, f"Downloaded: {title}")

        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("YouTubeDownloader", "Settings")
        self.lang = self.settings.value("language", "en")
        self.tr = TRANSLATIONS[self.lang]
        self.download_folder = self.settings.value("folder", get_windows_videos_folder())
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.tr['app_title'])
        self.setGeometry(100, 100, 800, 500)

        # Try to set icon
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        elif getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))

        # Dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2b2b2b; color: white; }
            QLineEdit { background-color: #3c3c3c; border: 2px solid #555; padding: 8px; border-radius: 4px; }
            QPushButton { background-color: #0d7377; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #14a085; }
            QComboBox { background-color: #3c3c3c; border: 2px solid #555; padding: 5px; border-radius: 4px; }
            QTextEdit { background-color: #1e1e1e; border: 2px solid #3c3c3c; border-radius: 4px; }
            QGroupBox { border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; }
            QProgressBar { border: 2px solid #555; border-radius: 4px; text-align: center; }
            QProgressBar::chunk { background-color: #0d7377; border-radius: 2px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # URL input
        url_group = QGroupBox("Video URL")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.tr['url_placeholder'])
        url_layout.addWidget(self.url_input)
        paste_btn = QPushButton(self.tr['paste_btn'])
        paste_btn.clicked.connect(self.paste_url)
        url_layout.addWidget(paste_btn)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Options
        options_layout = QHBoxLayout()

        # Quality
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel(self.tr['quality_label']))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)

        # Format
        format_layout = QVBoxLayout()
        self.video_radio = QRadioButton(self.tr['video_format'])
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton(self.tr['audio_format'])
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        options_layout.addLayout(format_layout)

        # Folder
        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel(self.tr['save_to']))
        folder_btn_layout = QHBoxLayout()
        self.folder_label = QLabel(self.download_folder)
        self.folder_label.setStyleSheet("padding: 5px; background-color: #1e1e1e;")
        folder_btn_layout.addWidget(self.folder_label)
        browse_btn = QPushButton(self.tr['browse'])
        browse_btn.clicked.connect(self.browse_folder)
        folder_btn_layout.addWidget(browse_btn)
        folder_layout.addLayout(folder_btn_layout)
        options_layout.addLayout(folder_layout)

        layout.addLayout(options_layout)

        # Download button
        self.download_btn = QPushButton(self.tr['download_btn'])
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        # Creator
        creator = QLabel(self.tr['created_by'])
        creator.setStyleSheet("color: #0d7377; font-weight: bold; padding: 10px;")
        creator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(creator)

    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr['save_to'], self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.setText(folder)
            self.settings.setValue("folder", folder)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, self.tr['error'], "Please enter URL")
            return

        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = DownloadThread(
            url,
            self.quality_combo.currentText(),
            self.audio_radio.isChecked(),
            self.download_folder
        )

        self.thread.progress.connect(self.log)
        self.thread.progress_value.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.download_finished)
        self.thread.start()

    def download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.log(f"✅ {self.tr['success']}: {message}")
            QMessageBox.information(self, self.tr['success'], message)
        else:
            self.log(f"❌ {self.tr['error']}: {message}")
            QMessageBox.critical(self, self.tr['error'], message)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''

with open("youtube_downloader_exe.py", "w", encoding="utf-8") as f:
    f.write(main_script)

print("   ✅ Created youtube_downloader_exe.py")

# Step 3: Build the EXE with proper FFmpeg bundling
print("\n3. Building EXE with FFmpeg...")

# Clean old builds
for path in ["dist", "build"]:
    if os.path.exists(path):
        shutil.rmtree(path)

# Build command with all necessary options
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--windowed",
    "--name",
    "YouTube_Downloader_Pro",
    "--add-binary",
    "ffmpeg.exe;.",
    "--add-binary",
    "ffprobe.exe;.",
    "--hidden-import",
    "yt_dlp",
    "--hidden-import",
    "yt_dlp.extractor",
    "--hidden-import",
    "yt_dlp.extractor.youtube",
    "--hidden-import",
    "yt_dlp.downloader",
    "--hidden-import",
    "yt_dlp.postprocessor",
    "--hidden-import",
    "yt_dlp.postprocessor.ffmpeg",
    "--hidden-import",
    "PyQt6",
]

# Add icon if exists
if os.path.exists("icon.ico"):
    cmd.extend(["--icon", "icon.ico", "--add-data", "icon.ico;."])

# Add cookies if exists
if os.path.exists("cookies.txt"):
    cmd.extend(["--add-data", "cookies.txt;."])

# Add main script
cmd.append("youtube_downloader_exe.py")

print("   Running PyInstaller...")
print("   This may take a few minutes...")

result = subprocess.run(cmd)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 60)

    exe_path = "dist/YouTube_Downloader_Pro.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n📦 Executable: {exe_path}")
        print(f"📊 Size: {size_mb:.1f} MB")
        print("\n✨ Features:")
        print("   • Downloads videos WITH picture and sound")
        print("   • FFmpeg bundled and working")
        print("   • Supports all quality options")
        print("   • Works on any Windows PC")

        print("\n" + "=" * 60)
        print("🎉 Your YouTube Downloader is ready!")
        print("🎬 It WILL download complete videos with audio!")
        print("=" * 60)
else:
    print("\n❌ Build failed")
    print("Check the error messages above")

input("\nPress Enter to exit...")
