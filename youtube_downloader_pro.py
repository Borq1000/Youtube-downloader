#!/usr/bin/env python3
"""
YouTube Downloader Pro
Created by Божидар Алемков
"""

import sys
import os

# Fix FFmpeg path when running as bundled EXE (PyInstaller)
if getattr(sys, "frozen", False):
    _bundle_dir = sys._MEIPASS
    os.environ["PATH"] = _bundle_dir + os.pathsep + os.environ.get("PATH", "")
    _ffmpeg = os.path.join(_bundle_dir, "ffmpeg.exe")
    if os.path.exists(_ffmpeg):
        os.environ["FFMPEG_BINARY"] = _ffmpeg
        os.environ["FFPROBE_BINARY"] = os.path.join(_bundle_dir, "ffprobe.exe")
import json
from datetime import datetime
from typing import Dict, Any

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
    QMessageBox,
    QTabWidget,
    QPlainTextEdit,
    QRadioButton,
    QSplitter,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

import yt_dlp


# Language translations
TRANSLATIONS = {
    "en": {
        "app_title": "YouTube Downloader Pro",
        "download_tab": "📥 Download",
        "settings_tab": "⚙️ Settings",
        "url_group": "Video URL",
        "url_placeholder": "Enter YouTube URL (e.g., https://youtube.com/watch?v=...)",
        "paste_btn": "📋 Paste from Clipboard",
        "quality_label": "Quality:",
        "video_format": "Video",
        "audio_format": "Audio Only (MP3)",
        "save_to": "Save to:",
        "browse": "Browse...",
        "download_btn": "🚀 Download",
        "status": "Status",
        "language_label": "🌐 Language / Язык:",
        "download_options": "Download Options",
        "proxy_title": "🌐 Proxy (for regions where YouTube is blocked)",
        "proxy_hint": "Leave empty if YouTube works without VPN/proxy",
        "proxy_protocol": "Protocol:",
        "proxy_ip": "IP:",
        "proxy_port": "Port:",
        "proxy_user": "User:",
        "proxy_password": "Password:",
        "proxy_saved": "Save",
        "proxy_cleared": "Clear",
        "proxy_test": "Test proxy",
        "proxy_testing": "Testing proxy connection...",
        "proxy_ok": "Proxy works!",
        "proxy_fail": "Proxy failed",
        "ffmpeg_title": "🎬 FFmpeg Status",
        "ffmpeg_found": "✅ FFmpeg installed (best quality available)",
        "ffmpeg_not_found": "⚠️ FFmpeg not found (limited quality)",
        "cookies_fallback_title": "🍪 Manual Cookies (fallback)",
        "cookies_fallback_hint": "Only needed if automatic authentication fails for private/age-restricted videos",
        "cookies_placeholder": "Paste cookies.txt content here...",
        "save_cookies": "💾 Save Cookies",
        "clear_cookies": "🗑️ Clear Cookies",
        "cookies_saved": "Cookies saved successfully!",
        "cookies_cleared": "Cookies cleared",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "please_enter_url": "Please enter a YouTube URL",
        "downloading": "Downloading",
        "download_complete": "Download complete",
        "download_failed": "Download failed",
        "created_by": "Created by: Божидар Алемков",
    },
    "ru": {
        "app_title": "YouTube Загрузчик Pro",
        "download_tab": "📥 Скачать",
        "settings_tab": "⚙️ Настройки",
        "url_group": "URL видео",
        "url_placeholder": "Введите URL YouTube (например, https://youtube.com/watch?v=...)",
        "paste_btn": "📋 Вставить из буфера",
        "quality_label": "Качество:",
        "video_format": "Видео",
        "audio_format": "Только аудио (MP3)",
        "save_to": "Сохранить в:",
        "browse": "Обзор...",
        "download_btn": "🚀 Скачать",
        "status": "Статус",
        "language_label": "🌐 Language / Язык:",
        "download_options": "Опции загрузки",
        "proxy_title": "🌐 Прокси (для регионов где YouTube заблокирован)",
        "proxy_hint": "Оставьте пустым если YouTube работает без VPN/прокси",
        "proxy_protocol": "Протокол:",
        "proxy_ip": "IP:",
        "proxy_port": "Порт:",
        "proxy_user": "Логин:",
        "proxy_password": "Пароль:",
        "proxy_saved": "Сохранить",
        "proxy_cleared": "Очистить",
        "proxy_test": "Проверить прокси",
        "proxy_testing": "Проверяю подключение через прокси...",
        "proxy_ok": "Прокси работает!",
        "proxy_fail": "Прокси не работает",
        "ffmpeg_title": "🎬 Статус FFmpeg",
        "ffmpeg_found": "✅ FFmpeg установлен (доступно лучшее качество)",
        "ffmpeg_not_found": "⚠️ FFmpeg не найден (ограниченное качество)",
        "cookies_fallback_title": "🍪 Ручные Cookies (запасной вариант)",
        "cookies_fallback_hint": "Нужно только если автоматическая аутентификация не работает для приватных/возрастных видео",
        "cookies_placeholder": "Вставьте содержимое cookies.txt сюда...",
        "save_cookies": "💾 Сохранить Cookies",
        "clear_cookies": "🗑️ Очистить Cookies",
        "cookies_saved": "Cookies успешно сохранены!",
        "cookies_cleared": "Cookies очищены",
        "success": "Успешно",
        "error": "Ошибка",
        "warning": "Предупреждение",
        "please_enter_url": "Пожалуйста, введите URL YouTube",
        "downloading": "Загрузка",
        "download_complete": "Загрузка завершена",
        "download_failed": "Ошибка загрузки",
        "created_by": "Создатель: Божидар Алемков",
    },
}


class DownloadThread(QThread):
    """Thread for downloading videos"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress_value = pyqtSignal(int)

    def __init__(self, url, quality, audio_only, output_dir, proxy=None):
        super().__init__()
        self.url = url
        self.quality = quality
        self.audio_only = audio_only
        self.output_dir = output_dir
        self.proxy = proxy

    def progress_hook(self, d):
        if d["status"] == "downloading":
            if "downloaded_bytes" in d and "total_bytes" in d:
                progress = int(d["downloaded_bytes"] * 100 / d["total_bytes"])
                self.progress_value.emit(progress)

            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            self.progress.emit(f"Progress: {percent} | Speed: {speed} | ETA: {eta}")

        elif d["status"] == "finished":
            self.progress.emit("Processing file...")

    def _build_base_opts(self):
        """Build base yt-dlp options without cookie config"""
        import shutil

        ydl_opts = {
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "merge_output_format": "mp4",
            "restrictfilenames": True,
            "windowsfilenames": True,
        }

        # Enable Node.js runtime for YouTube signature decryption
        if shutil.which("node"):
            ydl_opts["js_runtimes"] = {"node": {}}
            ydl_opts["remote_components"] = {"ejs:github": {}}

        # Proxy support
        if self.proxy:
            ydl_opts["proxy"] = self.proxy

        # Check FFmpeg and set location for EXE mode
        ffmpeg_available = self.check_ffmpeg()
        if ffmpeg_available and getattr(sys, "frozen", False):
            ydl_opts["ffmpeg_location"] = sys._MEIPASS
        elif ffmpeg_available and os.path.exists("ffmpeg.exe"):
            ydl_opts["ffmpeg_location"] = "."

        if self.audio_only:
            ydl_opts["format"] = "bestaudio/best"
            if ffmpeg_available:
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
        else:
            if ffmpeg_available:
                if self.quality == "best":
                    # Cap "best" at 1080p so we don't accidentally pull multi-GB
                    # 4K/8K streams (which look like a hang/failure on slow links).
                    ydl_opts["format"] = (
                        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/"
                        "best[height<=1080][ext=mp4]/best[height<=1080]/best"
                    )
                else:
                    height = self.quality[:-1]
                    ydl_opts["format"] = (
                        f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best"
                    )
            else:
                ydl_opts["format"] = "best[ext=mp4]/best"

        return ydl_opts

    def _detect_browsers(self):
        """Detect installed browsers for cookie extraction"""
        browsers = []
        browser_paths = {
            "chrome": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
            "edge": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"),
            "firefox": os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"),
            "brave": os.path.join(os.environ.get("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "User Data"),
            "opera": os.path.join(os.environ.get("APPDATA", ""), "Opera Software", "Opera Stable"),
        }
        for browser, path in browser_paths.items():
            if os.path.isdir(path):
                browsers.append(browser)
        return browsers

    def _try_download(self, ydl_opts):
        """Attempt a download, return (success, title_or_error)"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                return True, info.get("title", "Unknown")
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _is_network_error(error_msg):
        """Check if error is network-related (retrying with different cookies won't help)"""
        network_keywords = ["timed out", "timeout", "Connection refused",
                            "Network unreachable", "No route to host",
                            "getaddrinfo failed", "Name or service not known"]
        return any(kw.lower() in error_msg.lower() for kw in network_keywords)

    def run(self):
        ydl_opts = self._build_base_opts()

        # Step 1: Try with manual cookies.txt if it exists
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"
            self.progress.emit("Trying with saved cookies...")
            success, result = self._try_download(ydl_opts)
            if success:
                self.finished.emit(True, result)
                return
            self.progress.emit(f"Cookies failed: {result}")
            if self._is_network_error(result):
                self.finished.emit(False, f"Network error (check proxy/VPN): {result}")
                return
            del ydl_opts["cookiefile"]

        # Step 2: Try without any cookies (works for public videos)
        self.progress.emit("Trying without authentication...")
        success, result = self._try_download(ydl_opts)
        if success:
            self.finished.emit(True, result)
            return
        self.progress.emit(f"No-auth failed: {result}")

        # If network error, don't bother trying browsers — it won't help
        if self._is_network_error(result):
            self.finished.emit(False, f"Network error (check proxy/VPN): {result}")
            return

        # Step 3: Auto-extract cookies from installed browsers
        browsers = self._detect_browsers()
        for browser in browsers:
            self.progress.emit(f"Trying cookies from {browser}...")
            ydl_opts_browser = dict(ydl_opts)
            ydl_opts_browser["cookiesfrombrowser"] = (browser,)
            success, result = self._try_download(ydl_opts_browser)
            if success:
                self.finished.emit(True, result)
                return
            self.progress.emit(f"{browser} cookies failed: {result}")
            if self._is_network_error(result):
                self.finished.emit(False, f"Network error (check proxy/VPN): {result}")
                return

        # All attempts failed
        self.finished.emit(False, f"All download methods failed. Last error: {result}")

    def check_ffmpeg(self):
        import subprocess

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


class ProxyTestThread(QThread):
    """Quick test: try to reach YouTube through the proxy"""
    result = pyqtSignal(bool, str)

    def __init__(self, proxy_url):
        super().__init__()
        self.proxy_url = proxy_url

    def run(self):
        import shutil
        try:
            opts = {
                "proxy": self.proxy_url,
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 15,
            }
            if shutil.which("node"):
                opts["js_runtimes"] = {"node": {}}
                opts["remote_components"] = {"ejs:github": {}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract info from a short known video — just to test connectivity
                info = ydl.extract_info("https://www.youtube.com/watch?v=jNQXAC9IVRw", download=False)
                title = info.get("title", "OK")
                self.result.emit(True, title)
        except Exception as e:
            self.result.emit(False, str(e))


class YouTubeDownloaderPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("YouTubeDownloader", "ProSettings")
        self.current_lang = self.settings.value("language", "en")
        self.tr = TRANSLATIONS[self.current_lang]
        # Remember the last chosen download folder (defaults to ./downloads)
        self.output_dir = self.settings.value("output_dir", "downloads")
        self.download_thread = None
        self.init_ui()
        self.check_ffmpeg_status()

    def init_ui(self):
        self.setWindowTitle(self.tr["app_title"])
        self.setGeometry(100, 100, 900, 750)

        # Dark theme
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
            QLineEdit, QPlainTextEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QPlainTextEdit:focus {
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
            QLabel#creator {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #1e1e1e;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """
        )

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Download tab
        download_tab = self.create_download_tab()
        self.tabs.addTab(download_tab, self.tr["download_tab"])

        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, self.tr["settings_tab"])

        # Creator label at the bottom
        self.creator_label = QLabel(self.tr["created_by"])
        self.creator_label.setObjectName("creator")
        self.creator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.creator_label)

    def create_download_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # URL Input
        url_group = QGroupBox(self.tr["url_group"])
        url_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.tr["url_placeholder"])
        url_layout.addWidget(self.url_input)

        paste_btn = QPushButton(self.tr["paste_btn"])
        paste_btn.clicked.connect(self.paste_from_clipboard)
        url_layout.addWidget(paste_btn)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Options
        options_group = QGroupBox(self.tr["download_options"])
        options_layout = QHBoxLayout()

        # Quality
        quality_layout = QVBoxLayout()
        quality_label = QLabel(self.tr["quality_label"])
        quality_layout.addWidget(quality_label)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)

        # Format
        format_layout = QVBoxLayout()
        self.video_radio = QRadioButton(self.tr["video_format"])
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton(self.tr["audio_format"])
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        options_layout.addLayout(format_layout)

        # Output directory
        output_layout = QVBoxLayout()
        output_label = QLabel(self.tr["save_to"])
        output_layout.addWidget(output_label)
        self.output_label = QLabel(self.output_dir)
        self.output_label.setStyleSheet("padding: 5px; background-color: #1e1e1e;")
        self.output_label.setWordWrap(True)
        output_layout.addWidget(self.output_label)
        self.browse_btn = QPushButton(self.tr["browse"])
        self.browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.browse_btn)
        options_layout.addLayout(output_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Download button
        self.download_btn = QPushButton(self.tr["download_btn"])
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status log
        status_group = QGroupBox(self.tr["status"])
        status_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        status_layout.addWidget(self.log_text)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.tr["language_label"])
        lang_layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Русский"])
        self.lang_combo.setCurrentIndex(0 if self.current_lang == "en" else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        # Proxy section
        proxy_group = QGroupBox(self.tr["proxy_title"])
        proxy_layout = QVBoxLayout()

        proxy_hint = QLabel(self.tr["proxy_hint"])
        proxy_hint.setStyleSheet("color: #aaaaaa; padding: 2px 0;")
        proxy_layout.addWidget(proxy_hint)

        # Row 1: Protocol + IP + Port
        row1 = QHBoxLayout()

        row1.addWidget(QLabel(self.tr["proxy_protocol"]))
        self.proxy_protocol = QComboBox()
        self.proxy_protocol.addItems(["socks5", "socks4", "http", "https"])
        self.proxy_protocol.setCurrentText(self.settings.value("proxy_protocol", "socks5"))
        self.proxy_protocol.setMaximumWidth(100)
        row1.addWidget(self.proxy_protocol)

        row1.addWidget(QLabel(self.tr["proxy_ip"]))
        self.proxy_ip = QLineEdit()
        self.proxy_ip.setPlaceholderText("194.169.161.113")
        self.proxy_ip.setText(self.settings.value("proxy_ip", ""))
        row1.addWidget(self.proxy_ip)

        row1.addWidget(QLabel(self.tr["proxy_port"]))
        self.proxy_port = QLineEdit()
        self.proxy_port.setPlaceholderText("4539")
        self.proxy_port.setMaximumWidth(80)
        self.proxy_port.setText(self.settings.value("proxy_port", ""))
        row1.addWidget(self.proxy_port)

        proxy_layout.addLayout(row1)

        # Row 2: User + Password
        row2 = QHBoxLayout()

        row2.addWidget(QLabel(self.tr["proxy_user"]))
        self.proxy_user = QLineEdit()
        self.proxy_user.setPlaceholderText("user237271")
        self.proxy_user.setText(self.settings.value("proxy_user", ""))
        row2.addWidget(self.proxy_user)

        row2.addWidget(QLabel(self.tr["proxy_password"]))
        self.proxy_pass = QLineEdit()
        self.proxy_pass.setPlaceholderText("oid4wz")
        self.proxy_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.proxy_pass.setText(self.settings.value("proxy_pass", ""))
        row2.addWidget(self.proxy_pass)

        proxy_layout.addLayout(row2)

        # Buttons
        proxy_btn_layout = QHBoxLayout()
        save_proxy_btn = QPushButton(self.tr["proxy_saved"])
        save_proxy_btn.clicked.connect(self.save_proxy)
        proxy_btn_layout.addWidget(save_proxy_btn)

        clear_proxy_btn = QPushButton(self.tr["proxy_cleared"])
        clear_proxy_btn.clicked.connect(self.clear_proxy)
        proxy_btn_layout.addWidget(clear_proxy_btn)

        self.test_proxy_btn = QPushButton(self.tr["proxy_test"])
        self.test_proxy_btn.clicked.connect(self.test_proxy)
        proxy_btn_layout.addWidget(self.test_proxy_btn)

        proxy_btn_layout.addStretch()
        proxy_layout.addLayout(proxy_btn_layout)

        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # FFmpeg status
        ffmpeg_group = QGroupBox(self.tr["ffmpeg_title"])
        ffmpeg_layout = QVBoxLayout()
        self.ffmpeg_status_label = QLabel("Checking FFmpeg...")
        ffmpeg_layout.addWidget(self.ffmpeg_status_label)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)

        # Cookies fallback (collapsed by default)
        cookies_group = QGroupBox(self.tr["cookies_fallback_title"])
        cookies_group.setCheckable(True)
        cookies_group.setChecked(False)
        cookies_layout = QVBoxLayout()

        cookies_hint = QLabel(self.tr["cookies_fallback_hint"])
        cookies_hint.setWordWrap(True)
        cookies_hint.setStyleSheet("color: #aaaaaa; padding: 2px 0;")
        cookies_layout.addWidget(cookies_hint)

        self.cookies_text = QPlainTextEdit()
        self.cookies_text.setPlaceholderText(self.tr["cookies_placeholder"])
        self.cookies_text.setMaximumHeight(120)
        cookies_layout.addWidget(self.cookies_text)

        cookie_btn_layout = QHBoxLayout()
        save_cookies_btn = QPushButton(self.tr["save_cookies"])
        save_cookies_btn.clicked.connect(self.save_cookies)
        cookie_btn_layout.addWidget(save_cookies_btn)

        clear_cookies_btn = QPushButton(self.tr["clear_cookies"])
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        cookie_btn_layout.addWidget(clear_cookies_btn)

        cookies_layout.addLayout(cookie_btn_layout)
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)

        layout.addStretch()
        return tab

    def change_language(self, index):
        self.current_lang = "en" if index == 0 else "ru"
        self.settings.setValue("language", self.current_lang)
        self.tr = TRANSLATIONS[self.current_lang]

        QMessageBox.information(
            self,
            "Restart Required / Требуется перезапуск",
            "Please restart the application to apply language changes.\nПожалуйста, перезапустите приложение для применения изменений языка.",
        )

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
            self.log("URL pasted from clipboard")

    def browse_output(self):
        """Let the user pick the folder videos are saved to (persisted)."""
        start_dir = self.output_dir if os.path.isdir(self.output_dir) else os.path.expanduser("~")
        chosen = QFileDialog.getExistingDirectory(self, self.tr["save_to"], start_dir)
        if chosen:
            self.output_dir = chosen
            self.output_label.setText(chosen)
            self.settings.setValue("output_dir", chosen)
            self.log(f"{self.tr['save_to']} {chosen}")

    def _build_proxy_url(self):
        """Build proxy URL from individual fields"""
        ip = self.proxy_ip.text().strip()
        port = self.proxy_port.text().strip()
        if not ip or not port:
            return None
        protocol = self.proxy_protocol.currentText()
        user = self.proxy_user.text().strip()
        password = self.proxy_pass.text().strip()
        if user and password:
            return f"{protocol}://{user}:{password}@{ip}:{port}"
        return f"{protocol}://{ip}:{port}"

    def save_proxy(self):
        self.settings.setValue("proxy_protocol", self.proxy_protocol.currentText())
        self.settings.setValue("proxy_ip", self.proxy_ip.text().strip())
        self.settings.setValue("proxy_port", self.proxy_port.text().strip())
        self.settings.setValue("proxy_user", self.proxy_user.text().strip())
        self.settings.setValue("proxy_pass", self.proxy_pass.text().strip())
        proxy_url = self._build_proxy_url()
        self.log(self.tr["proxy_saved"] + (f": {self.proxy_ip.text().strip()}:{self.proxy_port.text().strip()}" if proxy_url else ""))

    def clear_proxy(self):
        self.proxy_ip.clear()
        self.proxy_port.clear()
        self.proxy_user.clear()
        self.proxy_pass.clear()
        for key in ["proxy_protocol", "proxy_ip", "proxy_port", "proxy_user", "proxy_pass"]:
            self.settings.setValue(key, "")
        self.log(self.tr["proxy_cleared"])

    def test_proxy(self):
        proxy_url = self._build_proxy_url()
        if not proxy_url:
            QMessageBox.warning(self, self.tr["warning"], "Fill in proxy IP and port first")
            return

        self.test_proxy_btn.setEnabled(False)
        self.log(self.tr["proxy_testing"])

        self._proxy_test_thread = ProxyTestThread(proxy_url)
        self._proxy_test_thread.result.connect(self._on_proxy_test_done)
        self._proxy_test_thread.start()

    def _on_proxy_test_done(self, success, message):
        self.test_proxy_btn.setEnabled(True)
        if success:
            self.log(f"{self.tr['proxy_ok']} ({message})")
            QMessageBox.information(self, self.tr["success"], f"{self.tr['proxy_ok']}\n{message}")
        else:
            self.log(f"{self.tr['proxy_fail']}: {message}")
            QMessageBox.critical(self, self.tr["error"], f"{self.tr['proxy_fail']}\n{message}")

    def save_cookies(self):
        cookies_content = self.cookies_text.toPlainText().strip()
        if not cookies_content:
            QMessageBox.warning(self, self.tr["warning"], "No cookies to save")
            return

        try:
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(cookies_content)

            self.cookies_status_label.setText(self.tr["cookies_found"])
            self.cookies_status_label.setStyleSheet(
                "color: #4CAF50; font-size: 16px; padding: 5px;"
            )
            QMessageBox.information(self, self.tr["success"], self.tr["cookies_saved"])
            self.log(self.tr["cookies_saved"])
        except Exception as e:
            QMessageBox.critical(self, self.tr["error"], str(e))

    def clear_cookies(self):
        self.cookies_text.clear()
        if os.path.exists("cookies.txt"):
            os.remove("cookies.txt")
        self.cookies_status_label.setText(self.tr["cookies_not_found"])
        self.cookies_status_label.setStyleSheet(
            "color: #FFA500; font-size: 16px; padding: 5px;"
        )
        self.log(self.tr["cookies_cleared"])

    def check_ffmpeg_status(self):
        import subprocess

        try:
            if os.path.exists("ffmpeg.exe"):
                result = subprocess.run(
                    ["ffmpeg.exe", "-version"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    self.ffmpeg_status_label.setText(self.tr["ffmpeg_found"])
                    self.ffmpeg_status_label.setStyleSheet("color: #4CAF50;")
                    return

            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                self.ffmpeg_status_label.setText(self.tr["ffmpeg_found"])
                self.ffmpeg_status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.ffmpeg_status_label.setText(self.tr["ffmpeg_not_found"])
                self.ffmpeg_status_label.setStyleSheet("color: #FFA500;")
        except:
            self.ffmpeg_status_label.setText(self.tr["ffmpeg_not_found"])
            self.ffmpeg_status_label.setStyleSheet("color: #FFA500;")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, self.tr["warning"], self.tr["please_enter_url"])
            return

        # Make sure the chosen output folder exists
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, self.tr["error"], f"{self.output_dir}\n{e}")
            return

        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        proxy = self._build_proxy_url()

        self.download_thread = DownloadThread(
            url,
            self.quality_combo.currentText(),
            self.audio_radio.isChecked(),
            self.output_dir,
            proxy=proxy,
        )

        self.download_thread.progress.connect(self.log)
        self.download_thread.progress_value.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

        self.log(f"{self.tr['downloading']}: {url}")

    def download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.log(f"✅ {self.tr['download_complete']}: {message}")
            QMessageBox.information(
                self, self.tr["success"], f"{self.tr['download_complete']}: {message}"
            )
        else:
            self.log(f"❌ {self.tr['download_failed']}: {message}")
            QMessageBox.critical(self, self.tr["error"], message)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Downloader Pro")

    window = YouTubeDownloaderPro()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
