# Weather Forecast Bot

Этот бот на `aiogram` предоставляет прогноз погоды для заданных маршрутов с возможностью выбора временного интервала прогноза.

## Запуск
```bash
cd bot
```
Создайте виртуальное окружение (рекомендуется):

```bash
python -m venv venv
source venv/bin/activate  # На Linux или macOS
venv\Scripts\activate  # На Windows
```
Установите зависимости:

```bash
pip install -r requirements.txt
```
Получите токен бота: Перейдите в BotFather в Telegram и создайте нового бота, чтобы получить токен.

Запуск бота

```bash
python main.py
```
Использование
Найдите вашего бота в Telegram и начните с ним диалог.
Введите команду /weather, чтобы начать процесс запроса прогноза погоды.
Введите начальную и конечную точки маршрута, когда бот запрашивает.
Выберите временной интервал прогноза (3 дня или 5 дней), используя инлайн-кнопки.
Бот отправит вам прогноз погоды.


# Веб-сервис прогноза погоды


## Установка Docker

1. **Скачайте и установите Docker**:
   - Перейдите на [официальный сайт Docker](https://www.docker.com/get-started).
   - Выберите вашу операционную систему (Windows, macOS или Linux) и следуйте инструкциям по установке.

2. **Проверьте установку Docker**:
   Откройте терминал или командную строку и выполните следующую команду:
   ```bash
   docker --version


## Запуск проекта
Перейдите в корень проекта (где находится файл compose.yaml) и выполните команду:
```bash
docker compose up --build
```

Откройте браузер и перейдите по адресу localhost
