#!/usr/bin/env python3
"""
Создание финального EXE файла с рабочим FFmpeg
Эта версия корректно скачивает видео со звуком
Created by Божидар Алемков
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
║     YouTube Downloader Pro - FINAL EXE Builder          ║
║         Создание EXE с рабочим FFmpeg                   ║
║              Created by Божидар Алемков                 ║
╚══════════════════════════════════════════════════════════╝
"""
)

# Шаг 1: Проверка и загрузка FFmpeg
print("\n📦 Шаг 1: Проверка FFmpeg...")
ffmpeg_exists = os.path.exists("ffmpeg.exe") and os.path.exists("ffprobe.exe")

if not ffmpeg_exists:
    print("   ⚠️  FFmpeg не найден. Загружаю...")

    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

    try:
        print("   📥 Загрузка FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")

        print("   📂 Распаковка...")
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
        print("   ✅ FFmpeg успешно загружен!")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки FFmpeg: {e}")
        print("\n   Пожалуйста, скачайте FFmpeg вручную:")
        print("   1. Перейдите на https://ffmpeg.org/download.html")
        print("   2. Скачайте Windows версию")
        print("   3. Распакуйте ffmpeg.exe и ffprobe.exe в текущую папку")
        input("\nНажмите Enter после размещения FFmpeg...")

        if not (os.path.exists("ffmpeg.exe") and os.path.exists("ffprobe.exe")):
            print("❌ FFmpeg не найден. Выход.")
            sys.exit(1)
else:
    print("   ✅ FFmpeg найден!")

# Проверка размера FFmpeg
ffmpeg_size = os.path.getsize("ffmpeg.exe") / (1024 * 1024)
ffprobe_size = os.path.getsize("ffprobe.exe") / (1024 * 1024)
print(f"   📊 Размер ffmpeg.exe: {ffmpeg_size:.1f} MB")
print(f"   📊 Размер ffprobe.exe: {ffprobe_size:.1f} MB")

# Шаг 2: Очистка старых сборок
print("\n🧹 Шаг 2: Очистка старых файлов...")
for path in ["dist", "build", "__pycache__"]:
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"   ✅ Удалено: {path}")

# Удаление старых spec файлов
for file in os.listdir("."):
    if file.endswith(".spec"):
        os.remove(file)
        print(f"   ✅ Удален spec файл: {file}")

# Шаг 3: Создание spec файла с правильной конфигурацией
print("\n📝 Шаг 3: Создание конфигурации сборки...")

spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Определяем файлы для включения
binaries = [
    ('ffmpeg.exe', '.'),
    ('ffprobe.exe', '.'),
]

datas = []

# Добавляем cookies если есть
import os
if os.path.exists('cookies.txt'):
    datas.append(('cookies.txt', '.'))

# Добавляем иконку если есть
if os.path.exists('icon.ico'):
    datas.append(('icon.ico', '.'))

a = Analysis(
    ['youtube_downloader_fix.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.downloader',
        'yt_dlp.downloader.http',
        'yt_dlp.downloader.dash',
        'yt_dlp.downloader.hls',
        'yt_dlp.postprocessor',
        'yt_dlp.postprocessor.ffmpeg',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube_Downloader_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Не сжимаем - может сломать FFmpeg
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""

with open("YouTube_Downloader.spec", "w", encoding="utf-8") as f:
    f.write(spec_content)
print("   ✅ Spec файл создан")

# Шаг 4: Создание runtime hook для FFmpeg
print("\n🔧 Шаг 4: Создание runtime hook...")

runtime_hook = """import sys
import os

# Устанавливаем пути FFmpeg при запуске EXE
if getattr(sys, 'frozen', False):
    # Запущено как EXE
    bundle_dir = sys._MEIPASS

    # Добавляем путь к FFmpeg в PATH
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

    # Устанавливаем переменные окружения для yt-dlp
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg.exe')
    ffprobe_path = os.path.join(bundle_dir, 'ffprobe.exe')

    if os.path.exists(ffmpeg_path):
        os.environ['FFMPEG_BINARY'] = ffmpeg_path
        print(f"FFmpeg set to: {ffmpeg_path}")

    if os.path.exists(ffprobe_path):
        os.environ['FFPROBE_BINARY'] = ffprobe_path
        print(f"FFprobe set to: {ffprobe_path}")
"""

with open("runtime_hook.py", "w", encoding="utf-8") as f:
    f.write(runtime_hook)
print("   ✅ Runtime hook создан")

# Шаг 5: Проверка наличия основного файла
print("\n📋 Шаг 5: Проверка файлов...")
if not os.path.exists("youtube_downloader_fix.py"):
    print("   ❌ Файл youtube_downloader_fix.py не найден!")
    print("   Используйте исправленную версию программы")
    sys.exit(1)
else:
    print("   ✅ Основной файл найден")

if os.path.exists("icon.ico"):
    icon_size = os.path.getsize("icon.ico") / 1024
    print(f"   ✅ Иконка найдена ({icon_size:.1f} KB)")
else:
    print("   ⚠️  Иконка не найдена (будет использована стандартная)")

if os.path.exists("cookies.txt"):
    print("   ✅ Файл cookies.txt будет включен")
else:
    print("   ⚠️  Файл cookies.txt не найден (нужно будет добавить в программе)")

# Шаг 6: Сборка EXE
print("\n🔨 Шаг 6: Сборка EXE файла...")
print("=" * 60)
print("Это может занять несколько минут...")
print("=" * 60)

# Запуск PyInstaller со spec файлом
cmd = [sys.executable, "-m", "PyInstaller", "--clean", "YouTube_Downloader.spec"]

print(f"\nКоманда: {' '.join(cmd)}\n")

result = subprocess.run(cmd)

# Проверка результата
if result.returncode == 0:
    print("\n" + "=" * 60)
    print("🎉 СБОРКА УСПЕШНО ЗАВЕРШЕНА!")
    print("=" * 60)

    exe_path = "dist/YouTube_Downloader_Pro.exe"
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)

        print(f"\n📦 Executable: {exe_path}")
        print(f"📊 Размер: {exe_size:.1f} MB")
        print("\n✨ Возможности:")
        print("   ✅ Скачивание видео С картинкой и звуком")
        print("   ✅ FFmpeg включен и работает")
        print("   ✅ Поддержка всех качеств (360p - 1080p+)")
        print("   ✅ Управление cookies")
        print("   ✅ Русский и английский язык")
        print("   ✅ Работает на любом Windows 10/11")

        print("\n" + "=" * 60)
        print("🚀 Ваш YouTube Downloader Pro готов к использованию!")
        print("🎬 Теперь видео скачивается ПРАВИЛЬНО со звуком!")
        print("=" * 60)

        # Опциональная очистка
        cleanup = input("\n🧹 Очистить временные файлы сборки? (y/n): ").lower()
        if cleanup == "y":
            for path in [
                "build",
                "__pycache__",
                "YouTube_Downloader.spec",
                "runtime_hook.py",
            ]:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"   ✅ Удалено: {path}")
            print("\n✅ Очистка завершена!")
    else:
        print(f"\n⚠️  EXE файл не найден в {exe_path}")
else:
    print("\n" + "=" * 60)
    print("❌ ОШИБКА СБОРКИ")
    print("=" * 60)
    print("\nВозможные причины:")
    print("1. Не установлен PyInstaller (pip install pyinstaller)")
    print("2. Проблемы с зависимостями")
    print("3. Антивирус блокирует создание EXE")
    print("\nПроверьте сообщения об ошибках выше")

input("\n📌 Нажмите Enter для выхода...")
