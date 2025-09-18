#!/bin/bash

# Скрипт для запуска приложения в Docker

echo "🚀 Запуск приложения tplVersionMonitoring в Docker..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл из .env.docker..."
    cp .env.docker .env
fi

# Собираем и запускаем контейнеры
echo "🔨 Сборка Docker образов..."
docker-compose build

echo "🚀 Запуск сервисов..."
docker-compose up -d

echo "⏳ Ожидание готовности базы данных..."
sleep 10

echo "📊 Выполнение миграций..."
docker-compose exec web python manage.py migrate

echo "👤 Создание суперпользователя (если нужно)..."
echo "Вы хотите создать суперпользователя? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

echo "✅ Приложение запущено!"
echo "🌐 Веб-интерфейс доступен по адресу: http://localhost:8000"
echo "📊 Админ-панель: http://localhost:8000/admin"
echo ""
echo "Для просмотра логов используйте: docker-compose logs -f"
echo "Для остановки: docker-compose down"
