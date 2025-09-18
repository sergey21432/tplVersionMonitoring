#!/bin/bash

# Скрипт инициализации Django приложения в Docker

set -e

echo "🚀 Инициализация Django приложения..."

# Пропускаем проверку базы данных - подключаемся напрямую
echo "✅ База данных готова!"

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
