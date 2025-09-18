#!/bin/bash

# Скрипт для запуска cron в Docker контейнере

echo "⏰ Настройка cron..."

# Устанавливаем crontab напрямую
(echo 'PATH=/usr/local/bin:/usr/bin:/bin'; echo '* * * * * cd /app && python manage.py check_template_updates >> /app/logs/cron.log 2>&1') | crontab -

echo "✅ Cron настроен!"
echo "📋 Установленные задачи:"
crontab -l

echo "🚀 Запуск cron-демона..."
exec cron -f
