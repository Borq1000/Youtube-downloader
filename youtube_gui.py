#!/usr/bin/env python3
"""
YouTube Downloader with PyQt6 GUI
Modern and user-friendly interface
"""

import sys
import os
import json
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import subprocess

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QComboBox,
    QProgressBar,
    QGroupBox,
    QRadioButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QListWidget,
    QSplitter,
    QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

import yt_dlp


@dataclass
class DownloadTask:
    url: str
    quality: str
    audio_only: bool
    output_dir: str


class CookieManager:
    """Manages browser cookies for YouTube authentication"""

    BROWSERS = ["chrome", "firefox", "edge", "brave", "opera", "chromium"]

    @staticmethod
    def get_cookies_from_browser(browser: str) -> bool:
        """Extract cookies from browser and save to file"""
        try:
            cmd = [
                "yt-dlp",
                "--cookies-from-browser",
                browser,
                "--cookies",
                "cookies.txt",
                "--skip-download",
                "https://www.youtube.com",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error getting cookies: {e}")
            return False

    @staticmethod
    def check_cookies_validity() -> tuple[bool, str]:
        """Check if cookies are valid"""
        if not os.path.exists("cookies.txt"):
            return False, "No cookies file found"

        # Check file age
        file_age = datetime.now().timestamp() - os.path.getmtime("cookies.txt")
        hours_old = file_age / 3600

        if hours_old > 24:
            return False, f"Cookies are {hours_old:.1f} hours old (may be expired)"

        return True, f"Cookies are {hours_old:.1f} hours old"


class DownloadThread(QThread):
    """Thread for downloading videos without blocking GUI"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    update_progress_bar = pyqtSignal(int)

    def __init__(self, task: DownloadTask, browser: str = None):
        super().__init__()
        self.task = task
        self.ydl = None
        self.browser = browser

    def progress_hook(self, d):
        """Called by yt-dlp during download"""
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")

            self.progress.emit(f"Downloading: {percent} | Speed: {speed} | ETA: {eta}")

            # Update progress bar
            if "downloaded_bytes" in d and "total_bytes" in d:
                progress = int(d["downloaded_bytes"] * 100 / d["total_bytes"])
                self.update_progress_bar.emit(progress)

        elif d["status"] == "finished":
            self.progress.emit("Processing downloaded file...")

    def run(self):
        """Run the download task"""
        try:
            ydl_opts = {
                "outtmpl": os.path.join(self.task.output_dir, "%(title)s.%(ext)s"),
                "quiet": False,
                "no_warnings": False,
                "progress_hooks": [self.progress_hook],
                "merge_output_format": "mp4",
                "restrictfilenames": True,
                "windowsfilenames": True,
            }

            # Enable Node.js runtime for YouTube signature decryption
            import shutil
            if shutil.which("node"):
                ydl_opts["js_runtimes"] = {"node": {}}
                ydl_opts["remote_components"] = {"ejs:github": {}}

            # Use browser cookies directly if specified, otherwise use cookies file
            if self.browser:
                ydl_opts["cookiesfrombrowser"] = (self.browser, None)
                self.progress.emit(f"Using cookies directly from {self.browser}")
            elif os.path.exists("cookies.txt"):
                ydl_opts["cookiefile"] = "cookies.txt"
                self.progress.emit("Using cookies from file")

            # Check for FFmpeg
            ffmpeg_available = self.check_ffmpeg()

            if self.task.audio_only:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
            else:
                if ffmpeg_available:
                    if self.task.quality == "best":
                        ydl_opts["format"] = (
                            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                        )
                    else:
                        height = self.task.quality[:-1]
                        ydl_opts["format"] = (
                            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best"
                        )
                else:
                    ydl_opts["format"] = "best[ext=mp4]/best"

            self.progress.emit(f"Starting download from: {self.task.url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.task.url, download=True)
                title = info.get("title", "Unknown")
                self.finished.emit(True, f"Successfully downloaded: {title}")

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            if os.path.exists("ffmpeg.exe"):
                result = subprocess.run(
                    ["ffmpeg.exe", "-version"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )
                return result.returncode == 0
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except:
            return False


class YouTubeDownloaderGUI(QMainWindow):
    """Main GUI Window"""

    def __init__(self):
        super().__init__()
        self.settings = QSettings("YouTubeDownloader", "Settings")
        self.download_thread = None
        self.init_ui()
        self.load_settings()
        self.check_cookies_status()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("YouTube Downloader Pro")
        self.setGeometry(100, 100, 900, 700)

        # Set modern dark theme
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #007ACC;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #007ACC;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 3px;
            }
            QTabWidget::pane {
                border: 2px solid #555555;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
            }
        """
        )

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Download tab
        download_tab = self.create_download_tab()
        self.tabs.addTab(download_tab, "📥 Download")

        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ Settings")

        # History tab
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "📜 History")

    def create_download_tab(self):
        """Create the main download tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # URL input section
        url_group = QGroupBox("Video URL")
        url_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Enter YouTube URL (e.g., https://youtube.com/watch?v=...)"
        )
        url_layout.addWidget(self.url_input)

        # Quick paste button
        paste_btn = QPushButton("📋 Paste from Clipboard")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        url_layout.addWidget(paste_btn)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Options section
        options_group = QGroupBox("Download Options")
        options_layout = QHBoxLayout()

        # Quality selection
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)

        # Format selection
        format_layout = QVBoxLayout()
        self.video_radio = QRadioButton("Video")
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton("Audio Only (MP3)")
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        options_layout.addLayout(format_layout)

        # Output directory
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Save to:"))

        output_btn_layout = QHBoxLayout()
        self.output_label = QLabel("downloads/")
        self.output_label.setStyleSheet("padding: 5px; background-color: #1e1e1e;")
        output_btn_layout.addWidget(self.output_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_btn_layout.addWidget(browse_btn)

        output_layout.addLayout(output_btn_layout)
        options_layout.addLayout(output_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Download button and progress
        self.download_btn = QPushButton("🚀 Download")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status/Log area
        log_group = QGroupBox("Status")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        return tab

    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Cookies section
        cookies_group = QGroupBox("🍪 Authentication (Cookies)")
        cookies_layout = QVBoxLayout()

        # Cookies status
        self.cookies_status_label = QLabel("Checking cookies status...")
        cookies_layout.addWidget(self.cookies_status_label)

        # Browser selection
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Browser:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(
            ["chrome", "firefox", "edge", "brave", "opera", "chromium"]
        )
        browser_layout.addWidget(self.browser_combo)
        cookies_layout.addLayout(browser_layout)

        # Cookie method selection
        self.use_browser_direct = QRadioButton(
            "Use cookies directly from browser (recommended)"
        )
        self.use_browser_direct.setChecked(True)
        self.use_cookie_file = QRadioButton("Use cookies from file")
        cookies_layout.addWidget(self.use_browser_direct)
        cookies_layout.addWidget(self.use_cookie_file)

        # Refresh cookies button
        refresh_btn = QPushButton("🔄 Refresh Cookies to File")
        refresh_btn.clicked.connect(self.refresh_cookies)
        cookies_layout.addWidget(refresh_btn)

        # Auto-refresh checkbox
        self.auto_refresh_check = QCheckBox("Auto-refresh cookies every 12 hours")
        cookies_layout.addWidget(self.auto_refresh_check)

        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)

        # FFmpeg section
        ffmpeg_group = QGroupBox("🎬 FFmpeg (for best quality)")
        ffmpeg_layout = QVBoxLayout()

        self.ffmpeg_status_label = QLabel("Checking FFmpeg...")
        ffmpeg_layout.addWidget(self.ffmpeg_status_label)

        install_ffmpeg_btn = QPushButton("Install FFmpeg")
        install_ffmpeg_btn.clicked.connect(self.install_ffmpeg)
        ffmpeg_layout.addWidget(install_ffmpeg_btn)

        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)

        # Check FFmpeg status
        self.check_ffmpeg_status()

        layout.addStretch()
        return tab

    def create_history_tab(self):
        """Create the download history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # History list
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        # Clear history button
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        # Load history
        self.load_history()

        return tab

    def paste_from_clipboard(self):
        """Paste URL from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
            self.log("Pasted URL from clipboard")

    def browse_output_dir(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if dir_path:
            self.output_label.setText(dir_path)
            self.settings.setValue("output_dir", dir_path)

    def start_download(self):
        """Start the download process"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL")
            return

        # Create download task
        task = DownloadTask(
            url=url,
            quality=self.quality_combo.currentText(),
            audio_only=self.audio_radio.isChecked(),
            output_dir=self.output_label.text(),
        )

        # Disable UI during download
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Determine which browser to use for cookies
        browser = None
        if self.use_browser_direct.isChecked():
            browser = self.browser_combo.currentText()
            self.log(f"Using cookies directly from {browser}")

        # Start download thread
        self.download_thread = DownloadThread(task, browser)
        self.download_thread.progress.connect(self.log)
        self.download_thread.update_progress_bar.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

        self.log(f"Starting download: {url}")

    def download_finished(self, success: bool, message: str):
        """Handle download completion"""
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.log(f"✅ {message}")
            self.add_to_history(self.url_input.text(), message)
            QMessageBox.information(self, "Success", message)
        else:
            self.log(f"❌ {message}")
            QMessageBox.critical(self, "Error", message)

    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def refresh_cookies(self):
        """Refresh cookies from selected browser"""
        browser = self.browser_combo.currentText()
        self.log(f"Refreshing cookies from {browser}...")

        if CookieManager.get_cookies_from_browser(browser):
            self.log(f"✅ Successfully refreshed cookies from {browser}")
            self.check_cookies_status()
            self.settings.setValue("last_browser", browser)
        else:
            self.log(f"❌ Failed to refresh cookies from {browser}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get cookies from {browser}.\n"
                "Make sure you're logged into YouTube in that browser.",
            )

    def check_cookies_status(self):
        """Check and display cookies status"""
        valid, message = CookieManager.check_cookies_validity()

        if valid:
            self.cookies_status_label.setText(f"✅ Cookies: {message}")
            self.cookies_status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.cookies_status_label.setText(f"⚠️ Cookies: {message}")
            self.cookies_status_label.setStyleSheet("color: #FFA500;")

            # Auto-refresh if enabled
            if self.auto_refresh_check.isChecked() and os.path.exists("cookies.txt"):
                file_age = (
                    datetime.now().timestamp() - os.path.getmtime("cookies.txt")
                ) / 3600
                if file_age > 12:
                    self.refresh_cookies()

    def check_ffmpeg_status(self):
        """Check if FFmpeg is installed"""
        try:
            if os.path.exists("ffmpeg.exe"):
                result = subprocess.run(
                    ["ffmpeg.exe", "-version"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    self.ffmpeg_status_label.setText(
                        "✅ FFmpeg is installed (best quality enabled)"
                    )
                    self.ffmpeg_status_label.setStyleSheet("color: #4CAF50;")
                    return

            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                self.ffmpeg_status_label.setText(
                    "✅ FFmpeg is installed (best quality enabled)"
                )
                self.ffmpeg_status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.ffmpeg_status_label.setText("⚠️ FFmpeg not found (limited quality)")
                self.ffmpeg_status_label.setStyleSheet("color: #FFA500;")
        except:
            self.ffmpeg_status_label.setText("⚠️ FFmpeg not found (limited quality)")
            self.ffmpeg_status_label.setStyleSheet("color: #FFA500;")

    def install_ffmpeg(self):
        """Install FFmpeg"""
        reply = QMessageBox.question(
            self,
            "Install FFmpeg",
            "This will download and install FFmpeg.\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log("Installing FFmpeg...")
            # Run the install_ffmpeg.py script
            try:
                subprocess.run([sys.executable, "install_ffmpeg.py"])
                self.check_ffmpeg_status()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to install FFmpeg: {e}")

    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def add_to_history(self, url: str, result: str):
        """Add download to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_item = f"{timestamp} - {url} - {result}"
        self.history_list.addItem(history_item)

        # Save to settings
        history = self.settings.value("history", [])
        if not isinstance(history, list):
            history = []
        history.append(history_item)
        # Keep only last 100 items
        history = history[-100:]
        self.settings.setValue("history", history)

    def load_history(self):
        """Load download history"""
        history = self.settings.value("history", [])
        if isinstance(history, list):
            for item in history:
                self.history_list.addItem(item)

    def clear_history(self):
        """Clear download history"""
        self.history_list.clear()
        self.settings.setValue("history", [])
        self.log("History cleared")

    def load_settings(self):
        """Load saved settings"""
        # Output directory
        output_dir = self.settings.value("output_dir", "downloads")
        self.output_label.setText(output_dir)

        # Last used browser
        last_browser = self.settings.value("last_browser", "chrome")
        index = self.browser_combo.findText(last_browser)
        if index >= 0:
            self.browser_combo.setCurrentIndex(index)

        # Auto-refresh setting
        auto_refresh = self.settings.value("auto_refresh", False, type=bool)
        self.auto_refresh_check.setChecked(auto_refresh)

    def closeEvent(self, event):
        """Save settings on close"""
        self.settings.setValue("auto_refresh", self.auto_refresh_check.isChecked())
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Downloader Pro")

    # Set application icon (if available)
    if os.path.exists("icon.png"):
        app.setWindowIcon(QIcon("icon.png"))

    window = YouTubeDownloaderGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
