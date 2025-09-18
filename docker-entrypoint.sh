#!/bin/bash

# Скрипт инициализации Django приложения в Docker

set -e

echo "🚀 Инициализация Django приложения..."

# Ждем готовности внешней базы данных
echo "⏳ Ожидание готовности внешней базы данных..."
python -c "
import psycopg2
import os
import time
import sys

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            database=os.getenv('DB_NAME', 'postgres')  # Подключаемся к нужной базе данных
        )
        conn.close()
        print('✅ Внешняя база данных готова!')
        break
    except psycopg2.OperationalError as e:
        retry_count += 1
        print(f'⏳ Попытка {retry_count}/{max_retries}: {e}')
        time.sleep(2)
else:
    print('❌ Не удалось подключиться к внешней базе данных')
    sys.exit(1)
"

# Выполняем миграции
echo "📊 Выполнение миграций..."
python manage.py migrate

# Собираем статические файлы
echo "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создаем суперпользователя если его нет
echo "👤 Проверка суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Создание суперпользователя...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Суперпользователь создан: admin/admin')
else:
    print('Суперпользователь уже существует')
"

echo "🎉 Инициализация завершена!"

# Запускаем команду, переданную в аргументах
exec "$@"
