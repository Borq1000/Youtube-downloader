# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Windows desktop YouTube video/audio downloader built with Python, PyQt6, and yt-dlp. Created by Bozhidar Alemkov. Supports English and Russian UI. Downloads go to a `downloads/` folder and authentication is handled via Netscape-format `cookies.txt`.

## Key Dependencies

- **yt-dlp** - YouTube video extraction and downloading
- **PyQt6** - GUI framework
- **FFmpeg** - required for best-quality video+audio merging and MP3 extraction (bundled as `ffmpeg.exe` in project root)

Install: `pip install -r requirements.txt` (yt-dlp and PyQt6 only; FFmpeg is a separate binary)

## Running the Application

```bash
# Main GUI variants (any one of these):
python youtube_downloader_pro.py   # Primary: manual cookie paste, EN/RU i18n
python youtube_gui.py              # Alternative: browser-based cookie extraction, download history tab
python youtube_downloader_fix.py   # Fixed version ensuring video+audio merge works
```

## Application Variants

There are multiple GUI entry points, each addressing different needs:

| File | Purpose |
|------|---------|
| `youtube_downloader_pro.py` | Manual cookie management via paste, EN/RU translations, two tabs (Download, Settings) |
| `youtube_gui.py` | Browser cookie extraction via yt-dlp `--cookies-from-browser`, download history tab, `CookieManager` class |
| `youtube_downloader_fix.py` | Fork of pro with bug fixes for video+audio merging |
| `youtube_downloader_exe.py` | Optimized for PyInstaller EXE bundling — patches `sys._MEIPASS` paths for FFmpeg at import time |

All variants share the same architecture: a `DownloadThread(QThread)` that runs yt-dlp in background with progress hooks, and a `QMainWindow` subclass with tabbed UI and dark theme stylesheet.

## Building the EXE

Multiple build scripts exist for packaging with PyInstaller:

```bash
python build_working_exe.py   # Recommended: downloads FFmpeg if missing, creates EXE with bundled FFmpeg
python build_exe.py           # Standard build with spec file generation
python create_final_exe.py    # Alternative builder
```

The built EXE lands in `dist/YouTube_Downloader_Pro.exe`. The EXE entry point is `youtube_downloader_exe.py`, which patches PATH/environment for bundled FFmpeg before importing yt-dlp.

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `install_ffmpeg.py` | Downloads FFmpeg binaries from GitHub to project root |
| `update_ytdlp.py` | `pip install --upgrade yt-dlp` |
| `test_download.py` | Interactive CLI test: prompts for URL, optional browser cookie extraction, verbose download |
| `test_ffmpeg.py` / `test_ffmpeg_exe.py` | Verify FFmpeg works standalone and inside the bundled EXE |
| `setup_ffmpeg.py` | Alternative FFmpeg setup |
| `fix_chrome_cookies.py` | Troubleshoot Chrome cookie extraction |
| `get_fresh_cookies.py` | Quick cookie refresh helper |

## Architecture Notes

- **Cookie authentication**: YouTube frequently requires authentication. The app supports two approaches: (1) manual paste of Netscape `cookies.txt` content via the Settings tab (`youtube_downloader_pro.py`), or (2) automatic extraction from a running browser via yt-dlp's `cookiesfrombrowser` option (`youtube_gui.py`).
- **FFmpeg detection**: Every variant checks for FFmpeg both as a local `ffmpeg.exe` in the project directory and on the system PATH. Without FFmpeg, only pre-muxed formats are available (lower quality).
- **Download thread pattern**: All variants use `QThread` with `pyqtSignal` for progress updates (`progress`, `finished`, `progress_value`/`update_progress_bar`) to keep the GUI responsive.
- **Settings persistence**: Uses `QSettings("YouTubeDownloader", ...)` for language preference, output directory, browser choice, and download history.
- **The `dlowder/` directory is an unrelated Django CMS project** — not part of this YouTube downloader application.
