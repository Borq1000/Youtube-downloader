#!/usr/bin/env python3
"""
YouTube Downloader Pro - ИСПРАВЛЕННАЯ ВЕРСИЯ
Эта версия правильно скачивает видео со звуком
Создано: Божидар Алемков
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

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
    QFileDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon

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
        "cookies_title": "🍪 Authentication (YouTube Cookies)",
        "cookies_status": "Cookie Status:",
        "cookies_found": "✅ Cookies loaded",
        "cookies_not_found": "❌ No cookies loaded",
        "cookies_instruction": "How to get YouTube cookies:",
        "instruction_1": '1. Install Chrome extension "Get cookies.txt LOCALLY"',
        "instruction_2": "2. Go to YouTube.com and log in to your account",
        "instruction_3": "3. Click the extension icon in Chrome",
        "instruction_4": '4. Click "Export" or "Export as cookies.txt"',
        "instruction_5": "5. Copy the text and paste it here",
        "paste_cookies": "Paste cookies here:",
        "save_cookies": "💾 Save Cookies",
        "clear_cookies": "🗑️ Clear Cookies",
        "language_label": "🌐 Language / Язык:",
        "theme_label": "🎨 Theme:",
        "dark_theme": "Dark",
        "light_theme": "Light",
        "created_by": "Created by: Божидар Алемков",
        "version": "Version: 3.1 Pro (Fixed)",
        "downloading": "Downloading",
        "converting": "Converting",
        "success": "Success",
        "error": "Error",
        "info": "Information",
        "warning": "Warning",
        "no_url": "Please enter a YouTube URL",
        "download_complete": "Download complete!",
        "download_failed": "Download failed",
        "cookies_saved": "Cookies saved successfully!",
        "cookies_cleared": "Cookies cleared successfully!",
        "cookies_invalid": "Invalid cookie format!",
        "ffmpeg_check": "Checking FFmpeg...",
        "ffmpeg_found": "✅ FFmpeg found",
        "ffmpeg_not_found": "⚠️ FFmpeg not found (limited quality options)",
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
        "cookies_title": "🍪 Авторизация (YouTube Cookies)",
        "cookies_status": "Статус cookies:",
        "cookies_found": "✅ Cookies загружены",
        "cookies_not_found": "❌ Cookies не загружены",
        "cookies_instruction": "Как получить YouTube cookies:",
        "instruction_1": '1. Установите расширение Chrome "Get cookies.txt LOCALLY"',
        "instruction_2": "2. Зайдите на YouTube.com и войдите в свой аккаунт",
        "instruction_3": "3. Нажмите на иконку расширения в Chrome",
        "instruction_4": '4. Нажмите "Export" или "Экспортировать как cookies.txt"',
        "instruction_5": "5. Скопируйте текст и вставьте сюда",
        "paste_cookies": "Вставьте cookies сюда:",
        "save_cookies": "💾 Сохранить Cookies",
        "clear_cookies": "🗑️ Очистить Cookies",
        "language_label": "🌐 Язык / Language:",
        "theme_label": "🎨 Тема:",
        "dark_theme": "Темная",
        "light_theme": "Светлая",
        "created_by": "Создатель: Божидар Алемков",
        "version": "Версия: 3.1 Pro (Исправлено)",
        "downloading": "Загрузка",
        "converting": "Конвертация",
        "success": "Успешно",
        "error": "Ошибка",
        "info": "Информация",
        "warning": "Предупреждение",
        "no_url": "Пожалуйста, введите URL YouTube",
        "download_complete": "Загрузка завершена!",
        "download_failed": "Ошибка загрузки",
        "cookies_saved": "Cookies успешно сохранены!",
        "cookies_cleared": "Cookies успешно очищены!",
        "cookies_invalid": "Неверный формат cookies!",
        "ffmpeg_check": "Проверка FFmpeg...",
        "ffmpeg_found": "✅ FFmpeg найден",
        "ffmpeg_not_found": "⚠️ FFmpeg не найден (ограниченные опции качества)",
    },
}


def get_windows_videos_folder():
    """Get Windows Videos folder (supports Russian Windows)"""
    possible_paths = [
        Path.home() / "Videos",
        Path.home() / "Видео",
        Path("C:/Users") / os.environ.get("USERNAME", "") / "Videos",
        Path("C:/Users") / os.environ.get("USERNAME", "") / "Видео",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    # Create Videos folder if it doesn't exist
    videos_folder = Path.home() / "Videos"
    videos_folder.mkdir(exist_ok=True)
    return str(videos_folder)


def check_ffmpeg():
    """Check if FFmpeg is available"""
    import subprocess

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=2
        )
        return result.returncode == 0
    except:
        # Try Windows-specific paths
        ffmpeg_paths = [
            "ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
        ]
        for path in ffmpeg_paths:
            if os.path.exists(path):
                return True
        return False


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
        if d["status"] == "downloading":
            # Update progress bar
            if "downloaded_bytes" in d and "total_bytes" in d:
                progress = int(d["downloaded_bytes"] * 100 / d["total_bytes"])
                self.progress_value.emit(progress)

            # Format progress message
            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            self.progress.emit(f"Downloading: {percent} | Speed: {speed} | ETA: {eta}")
        elif d["status"] == "finished":
            self.progress.emit("Processing downloaded file...")

    def run(self):
        try:
            # Base options
            ydl_opts = {
                "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "restrictfilenames": True,
                "windowsfilenames": True,
                "nocheckcertificate": True,
                "quiet": False,
                "no_warnings": False,
            }

            # Enable Node.js runtime for YouTube signature decryption
            import shutil
            if shutil.which("node"):
                ydl_opts["js_runtimes"] = {"node": {}}
                ydl_opts["remote_components"] = {"ejs:github": {}}

            # Load cookies if available
            cookie_file = "cookies.txt"
            if os.path.exists(cookie_file):
                ydl_opts["cookiefile"] = cookie_file
                self.progress.emit("Using cookies for authentication")

            # Check for FFmpeg
            ffmpeg_available = check_ffmpeg()
            if ffmpeg_available:
                self.progress.emit("FFmpeg detected - best quality available")
                # Set FFmpeg location if local
                if os.path.exists("ffmpeg.exe"):
                    ydl_opts["ffmpeg_location"] = os.path.dirname(
                        os.path.abspath(__file__)
                    )
            else:
                self.progress.emit("FFmpeg not found - using fallback formats")

            if self.audio_only:
                # Audio only - this works correctly
                ydl_opts["format"] = "bestaudio/best"
                if ffmpeg_available:
                    ydl_opts["postprocessors"] = [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ]
                self.progress.emit("Downloading audio only...")
            else:
                # VIDEO - ВАЖНОЕ ИСПРАВЛЕНИЕ!
                # Проблема была в том, что мы неправильно указывали формат

                if ffmpeg_available:
                    # С FFmpeg - можем объединить лучшее видео и аудио
                    # ИСПРАВЛЕНИЕ: Используем правильный синтаксис для yt-dlp
                    if self.quality == "best":
                        # Скачиваем лучшее качество видео + аудио
                        ydl_opts["format"] = (
                            "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
                        )
                    elif self.quality == "1080p":
                        ydl_opts["format"] = (
                            "(bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a])/best[height<=1080]/best"
                        )
                    elif self.quality == "720p":
                        ydl_opts["format"] = (
                            "(bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a])/best[height<=720]/best"
                        )
                    elif self.quality == "480p":
                        ydl_opts["format"] = (
                            "(bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a])/best[height<=480]/best"
                        )
                    elif self.quality == "360p":
                        ydl_opts["format"] = (
                            "(bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a])/best[height<=360]/best"
                        )
                    else:
                        ydl_opts["format"] = "best"

                    # ВАЖНО: Добавляем merge_output_format для правильного объединения
                    ydl_opts["merge_output_format"] = "mp4"

                    # Добавляем постпроцессор для конвертации в MP4 если нужно
                    ydl_opts["postprocessors"] = [
                        {
                            "key": "FFmpegVideoConvertor",
                            "preferedformat": "mp4",
                        }
                    ]

                    self.progress.emit(
                        f"Downloading {self.quality} video with audio (using FFmpeg)..."
                    )
                else:
                    # Без FFmpeg - используем форматы которые уже содержат видео И аудио
                    # Format 22 = 720p mp4 (содержит и видео и аудио)
                    # Format 18 = 360p mp4 (содержит и видео и аудио)

                    if self.quality == "best" or self.quality == "720p":
                        ydl_opts["format"] = "22/best[ext=mp4]/best"
                    elif self.quality == "1080p":
                        # Без FFmpeg не можем получить 1080p с аудио, используем 720p
                        ydl_opts["format"] = "22/best[ext=mp4]/best"
                        self.progress.emit(
                            "Note: 1080p requires FFmpeg, using 720p instead"
                        )
                    elif self.quality == "480p" or self.quality == "360p":
                        ydl_opts["format"] = "18/worst[ext=mp4]/worst"
                    else:
                        ydl_opts["format"] = "22/18/best"

                    self.progress.emit(
                        f"Downloading {self.quality} video (pre-merged format)..."
                    )

            # ВАЖНО: Логирование для отладки
            self.progress.emit(f"Format string: {ydl_opts.get('format', 'default')}")

            # Download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress.emit(f"Starting download: {self.url}")

                # Сначала получаем информацию о видео
                info = ydl.extract_info(self.url, download=False)

                # Логируем доступные форматы для отладки
                formats = info.get("formats", [])
                video_formats = []
                audio_formats = []
                combined_formats = []

                for f in formats:
                    format_note = f.get("format_note", "N/A")
                    format_id = f.get("format_id", "N/A")
                    ext = f.get("ext", "N/A")
                    vcodec = f.get("vcodec", "none")
                    acodec = f.get("acodec", "none")

                    if vcodec != "none" and acodec != "none":
                        combined_formats.append(f"{format_id} ({format_note}, {ext})")
                    elif vcodec != "none":
                        video_formats.append(f"{format_id} ({format_note}, {ext})")
                    elif acodec != "none":
                        audio_formats.append(f"{format_id} ({format_note}, {ext})")

                if combined_formats:
                    self.progress.emit(
                        f"Found formats with video+audio: {', '.join(combined_formats[:3])}"
                    )
                else:
                    self.progress.emit(
                        "No pre-merged formats found, will need FFmpeg to combine"
                    )

                # Теперь скачиваем
                info = ydl.extract_info(self.url, download=True)

                # Get title for success message
                title = info.get("title", "Unknown")

                # Проверяем какой формат был скачан
                requested_format = info.get("format", "N/A")
                self.progress.emit(f"Downloaded format: {requested_format}")

                self.finished.emit(True, title)

        except Exception as e:
            error_msg = str(e)
            # Добавляем больше информации об ошибке
            if "ffmpeg" in error_msg.lower():
                error_msg += "\n\nFFmpeg is required for this quality. Please install FFmpeg or choose a lower quality."
            self.finished.emit(False, error_msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("YouTubeDownloader", "Settings")
        self.current_language = self.settings.value("language", "en")
        self.tr = TRANSLATIONS[self.current_language]
        self.download_folder = self.settings.value(
            "download_folder", get_windows_videos_folder()
        )

        self.init_ui()
        self.check_cookies()
        self.check_ffmpeg_status()

    def init_ui(self):
        self.setWindowTitle(self.tr["app_title"])
        self.setGeometry(100, 100, 900, 700)

        # Set icon if exists
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))

        # Apply dark theme
        self.apply_dark_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Download tab
        self.download_tab = QWidget()
        self.setup_download_tab()
        self.tabs.addTab(self.download_tab, self.tr["download_tab"])

        # Settings tab
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.settings_tab, self.tr["settings_tab"])

        # Status bar
        self.statusBar().showMessage(self.tr["created_by"] + " | " + self.tr["version"])

    def apply_dark_theme(self):
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 2px solid #3c3c3c;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 10px 20px;
            margin: 2px;
            border-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #0d7377;
        }
        QLineEdit {
            background-color: #3c3c3c;
            border: 2px solid #555;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border-color: #0d7377;
        }
        QPushButton {
            background-color: #0d7377;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #14a085;
        }
        QPushButton:pressed {
            background-color: #0a5d61;
        }
        QPushButton:disabled {
            background-color: #555;
        }
        QComboBox {
            background-color: #3c3c3c;
            border: 2px solid #555;
            padding: 5px;
            border-radius: 4px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            border: 2px solid #3c3c3c;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        QGroupBox {
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QProgressBar {
            border: 2px solid #555;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #0d7377;
            border-radius: 2px;
        }
        QRadioButton {
            spacing: 10px;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
        }
        QRadioButton::indicator:checked {
            background-color: #0d7377;
            border: 2px solid #0d7377;
            border-radius: 9px;
        }
        QRadioButton::indicator:unchecked {
            background-color: #3c3c3c;
            border: 2px solid #555;
            border-radius: 9px;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #0d7377;
        }
        """
        self.setStyleSheet(dark_style)

    def setup_download_tab(self):
        layout = QVBoxLayout(self.download_tab)

        # URL input group
        url_group = QGroupBox(self.tr["url_group"])
        url_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.tr["url_placeholder"])
        url_layout.addWidget(self.url_input)

        paste_btn = QPushButton(self.tr["paste_btn"])
        paste_btn.clicked.connect(self.paste_url)
        url_layout.addWidget(paste_btn)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Options group
        options_group = QGroupBox("Download Options")
        options_layout = QHBoxLayout()

        # Quality selection
        quality_layout = QVBoxLayout()
        quality_label = QLabel(self.tr["quality_label"])
        quality_layout.addWidget(quality_label)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)

        # Format selection
        format_layout = QVBoxLayout()
        format_label = QLabel("Format:")
        format_layout.addWidget(format_label)

        self.video_radio = QRadioButton(self.tr["video_format"])
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton(self.tr["audio_format"])

        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        options_layout.addLayout(format_layout)

        # Save location
        save_layout = QVBoxLayout()
        save_label = QLabel(self.tr["save_to"])
        save_layout.addWidget(save_label)

        folder_layout = QHBoxLayout()
        self.folder_label = QLabel(self.download_folder)
        self.folder_label.setStyleSheet(
            "padding: 5px; background-color: #1e1e1e; border: 1px solid #555;"
        )
        folder_layout.addWidget(self.folder_label)

        browse_btn = QPushButton(self.tr["browse"])
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)

        save_layout.addLayout(folder_layout)
        options_layout.addLayout(save_layout)

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

        # Status/Log area
        status_group = QGroupBox(self.tr["status"])
        status_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        status_layout.addWidget(self.log_text)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Add stretch to push everything up
        layout.addStretch()

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)

        # Cookie settings group
        cookies_group = QGroupBox(self.tr["cookies_title"])
        cookies_layout = QVBoxLayout()

        # Cookie status
        self.cookie_status = QLabel(self.tr["cookies_not_found"])
        self.cookie_status.setStyleSheet(
            "padding: 10px; background-color: #1e1e1e; border-radius: 4px;"
        )
        cookies_layout.addWidget(self.cookie_status)

        # Instructions
        instructions = QLabel(
            f"{self.tr['cookies_instruction']}\n\n"
            f"{self.tr['instruction_1']}\n"
            f"{self.tr['instruction_2']}\n"
            f"{self.tr['instruction_3']}\n"
            f"{self.tr['instruction_4']}\n"
            f"{self.tr['instruction_5']}"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "padding: 10px; background-color: #1e1e1e; border-radius: 4px;"
        )
        cookies_layout.addWidget(instructions)

        # Cookie input
        cookie_label = QLabel(self.tr["paste_cookies"])
        cookies_layout.addWidget(cookie_label)

        self.cookie_text = QPlainTextEdit()
        self.cookie_text.setMaximumHeight(150)
        cookies_layout.addWidget(self.cookie_text)

        # Cookie buttons
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

        # Language settings
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.tr["language_label"])
        lang_layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Русский"])
        self.lang_combo.setCurrentIndex(0 if self.current_language == "en" else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()

        layout.addLayout(lang_layout)

        # FFmpeg status
        self.ffmpeg_status = QLabel()
        self.ffmpeg_status.setStyleSheet(
            "padding: 10px; background-color: #1e1e1e; border-radius: 4px;"
        )
        layout.addWidget(self.ffmpeg_status)

        # Add stretch
        layout.addStretch()

        # Creator info
        creator_info = QLabel(
            f"<h3>{self.tr['created_by']}</h3>" f"<p>{self.tr['version']}</p>"
        )
        creator_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creator_info.setStyleSheet("color: #0d7377; padding: 20px;")
        layout.addWidget(creator_info)

    def check_cookies(self):
        """Check if cookies.txt exists"""
        if os.path.exists("cookies.txt"):
            self.cookie_status.setText(self.tr["cookies_found"])
            self.cookie_status.setStyleSheet(
                "padding: 10px; background-color: #1e1e1e; border-radius: 4px; color: #4CAF50;"
            )

            # Load cookies to display
            try:
                with open("cookies.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                    self.cookie_text.setPlainText(
                        content[:500] + "..." if len(content) > 500 else content
                    )
            except:
                pass
        else:
            self.cookie_status.setText(self.tr["cookies_not_found"])
            self.cookie_status.setStyleSheet(
                "padding: 10px; background-color: #1e1e1e; border-radius: 4px; color: #f44336;"
            )

    def check_ffmpeg_status(self):
        """Check FFmpeg availability"""
        if check_ffmpeg():
            self.ffmpeg_status.setText(self.tr["ffmpeg_found"])
            self.ffmpeg_status.setStyleSheet(
                "padding: 10px; background-color: #1e1e1e; border-radius: 4px; color: #4CAF50;"
            )
        else:
            self.ffmpeg_status.setText(self.tr["ffmpeg_not_found"])
            self.ffmpeg_status.setStyleSheet(
                "padding: 10px; background-color: #1e1e1e; border-radius: 4px; color: #FFA500;"
            )

    def paste_url(self):
        """Paste URL from clipboard"""
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())

    def browse_folder(self):
        """Select download folder"""
        folder = QFileDialog.getExistingDirectory(
            self, self.tr["save_to"], self.download_folder
        )
        if folder:
            self.download_folder = folder
            self.folder_label.setText(folder)
            self.settings.setValue("download_folder", folder)

    def save_cookies(self):
        """Save cookies to file"""
        cookie_content = self.cookie_text.toPlainText().strip()

        if not cookie_content:
            QMessageBox.warning(self, self.tr["warning"], self.tr["cookies_invalid"])
            return

        try:
            # Save to cookies.txt
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(cookie_content)

            self.check_cookies()
            QMessageBox.information(self, self.tr["info"], self.tr["cookies_saved"])
            self.log(self.tr["cookies_saved"])
        except Exception as e:
            QMessageBox.critical(
                self, self.tr["error"], f"Error saving cookies: {str(e)}"
            )

    def clear_cookies(self):
        """Clear cookies"""
        try:
            if os.path.exists("cookies.txt"):
                os.remove("cookies.txt")
            self.cookie_text.clear()
            self.check_cookies()
            QMessageBox.information(self, self.tr["info"], self.tr["cookies_cleared"])
            self.log(self.tr["cookies_cleared"])
        except Exception as e:
            QMessageBox.critical(
                self, self.tr["error"], f"Error clearing cookies: {str(e)}"
            )

    def change_language(self, index):
        """Change interface language"""
        new_lang = "en" if index == 0 else "ru"
        if new_lang != self.current_language:
            self.current_language = new_lang
            self.settings.setValue("language", new_lang)
            self.tr = TRANSLATIONS[new_lang]

            # Update all UI elements
            self.update_translations()

    def update_translations(self):
        """Update all UI text with new language"""
        # Window title
        self.setWindowTitle(self.tr["app_title"])

        # Tab titles
        self.tabs.setTabText(0, self.tr["download_tab"])
        self.tabs.setTabText(1, self.tr["settings_tab"])

        # Update all labels and buttons
        self.url_input.setPlaceholderText(self.tr["url_placeholder"])

        # Find and update all buttons and labels
        for widget in self.findChildren(QPushButton):
            text = widget.text()
            if "📋" in text:
                widget.setText(self.tr["paste_btn"])
            elif "🚀" in text:
                widget.setText(self.tr["download_btn"])
            elif "💾" in text:
                widget.setText(self.tr["save_cookies"])
            elif "🗑️" in text:
                widget.setText(self.tr["clear_cookies"])

        # Update status bar
        self.statusBar().showMessage(self.tr["created_by"] + " | " + self.tr["version"])

        # Check statuses again to update language
        self.check_cookies()
        self.check_ffmpeg_status()

    def start_download(self):
        """Start download process"""
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, self.tr["warning"], self.tr["no_url"])
            return

        # Disable download button
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear log
        self.log_text.clear()
        self.log(f"{self.tr['downloading']}: {url}")

        # Create download thread
        self.download_thread = DownloadThread(
            url,
            self.quality_combo.currentText(),
            self.audio_radio.isChecked(),
            self.download_folder,
        )

        # Connect signals
        self.download_thread.progress.connect(self.log)
        self.download_thread.progress_value.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_finished)

        # Start download
        self.download_thread.start()

    def download_finished(self, success, message):
        """Handle download completion"""
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.log(f"✅ {self.tr['success']}: {message}")
            QMessageBox.information(
                self,
                self.tr["download_complete"],
                f"{self.tr['download_complete']}\n{message}",
            )
        else:
            self.log(f"❌ {self.tr['error']}: {message}")
            QMessageBox.critical(
                self,
                self.tr["download_failed"],
                f"{self.tr['download_failed']}\n{message}",
            )

    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
