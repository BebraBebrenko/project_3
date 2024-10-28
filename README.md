# Запуск проекта

## Проверка API ключа

Чтобы запустить скрипт проверки ключа, перейдите в папку scripts и запустите test.py

```bash
cd scripts
pip install -r requirements.txt
python test.py
```

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
