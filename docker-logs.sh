#!/bin/bash

# Скрипт для просмотра логов

echo "📋 Просмотр логов приложения..."

if [ "$1" = "web" ]; then
    docker-compose logs -f web
elif [ "$1" = "db" ]; then
    docker-compose logs -f db
elif [ "$1" = "cron" ]; then
    docker-compose logs -f cron
else
    docker-compose logs -f
fi
