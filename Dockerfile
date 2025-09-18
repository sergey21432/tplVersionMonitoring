# Используем официальный Python образ
FROM python:3.13.7-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Копируем скрипт инициализации
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Копируем скрипт для cron
COPY start-cron.sh /app/
RUN chmod +x /app/start-cron.sh

# Создаем директорию для логов
RUN mkdir -p logs

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Используем entrypoint скрипт
ENTRYPOINT ["docker-entrypoint.sh"]

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
