# Как получить cookies для YouTube

## Способ 1: Расширение браузера (Рекомендуется)

1. **Установите расширение "Get cookies.txt LOCALLY"**
   - [Для Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Для Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)

2. **Войдите в YouTube**
   - Откройте https://youtube.com
   - Войдите в свой аккаунт Google

3. **Экспортируйте cookies**
   - Нажмите на иконку расширения
   - Выберите "Export cookies.txt"
   - Сохраните файл как `cookies.txt` в папку с программой

## Способ 2: Используя yt-dlp

Запустите в командной строке:

```bash
# Для Chrome
yt-dlp --cookies-from-browser chrome --cookies cookies.txt https://youtube.com

# Для Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt https://youtube.com

# Для Edge
yt-dlp --cookies-from-browser edge --cookies cookies.txt https://youtube.com
```

## Способ 3: Ручной экспорт (продвинутый)

1. Откройте YouTube и войдите в аккаунт
2. Нажмите F12 для открытия инструментов разработчика
3. Перейдите на вкладку Application/Storage
4. Найдите Cookies → youtube.com
5. Экспортируйте в формате Netscape cookies.txt

## Проверка

После создания файла `cookies.txt`:
- Поместите его в папку с программой
- Запустите программу - она автоматически обнаружит и использует cookies
- В меню выберите опцию 5 для проверки статуса

## Безопасность

⚠️ **ВАЖНО**: Файл cookies содержит данные вашей сессии.
- Не делитесь этим файлом с другими
- Храните его в безопасном месте
- Периодически обновляйте (cookies могут истечь)

## Устранение проблем

Если скачивание все еще не работает:
1. Убедитесь, что вы вошли в YouTube в браузере
2. Проверьте, что файл называется именно `cookies.txt`
3. Обновите cookies (они могут устареть)
4. Попробуйте другой браузер/метод экспорта