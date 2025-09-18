# Развертывание tplVersionMonitoring через Docker

Этот документ описывает процесс развертывания приложения мониторинга версий шаблонов с использованием Docker.

## Предварительные требования

- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose
- Минимум 2GB свободного места на диске

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Перейдите в директорию проекта
cd tplVersionMonitoring

# Сделайте скрипты исполняемыми (Linux/Mac)
chmod +x docker-*.sh
```

### 2. Настройка переменных окружения

Скопируйте файл с настройками по умолчанию:
```bash
cp .env.docker .env
```

Отредактируйте файл `.env` под ваши нужды:
```env
# Настройки базы данных
DB_NAME=postgres
DB_USER=p4e_tpl_version_monitoring
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

# Настройки Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Настройки Mattermost
MATTERMOST_WEBHOOK_URL=https://your-mattermost-server.com/hooks/your-webhook-id
MATTERMOST_CHANNEL=template-updates
```

### 3. Запуск приложения

Используйте готовый скрипт:
```bash
./docker-start.sh
```

Или запустите вручную:
```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Выполнение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## Структура сервисов

### web
- **Порт**: 8000
- **Описание**: Django веб-приложение
- **URL**: http://localhost:8000

### db
- **Порт**: 5432
- **Описание**: PostgreSQL база данных
- **Данные**: Сохраняются в Docker volume `postgres_data`

### cron
- **Описание**: Автоматическая проверка обновлений каждые 6 часов
- **Команда**: `python manage.py check_template_updates`

## Управление приложением

### Просмотр логов
```bash
# Все сервисы
./docker-logs.sh

# Конкретный сервис
./docker-logs.sh web
./docker-logs.sh db
./docker-logs.sh cron
```

### Остановка приложения
```bash
./docker-stop.sh
```

### Выполнение команд Django
```bash
# Миграции
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Проверка обновлений шаблонов
docker-compose exec web python manage.py check_template_updates

# Добавление нового шаблона
docker-compose exec web python manage.py add_template --code TEMPLATE_CODE --version 1.0.0
```

### Доступ к базе данных
```bash
# Подключение к PostgreSQL
docker-compose exec db psql -U p4e_tpl_version_monitoring -d postgres
```

## Настройка для продакшена

### 1. Безопасность
- Измените `SECRET_KEY` на уникальный
- Установите `DEBUG=False`
- Настройте `ALLOWED_HOSTS` в settings.py

### 2. База данных
- Используйте внешнюю PostgreSQL базу данных
- Настройте резервное копирование

### 3. Веб-сервер
- Используйте Nginx как reverse proxy
- Настройте SSL сертификаты

### 4. Мониторинг
- Настройте логирование
- Добавьте мониторинг здоровья контейнеров

## Решение проблем

### Проблемы с подключением к базе данных
```bash
# Проверьте статус контейнеров
docker-compose ps

# Проверьте логи базы данных
docker-compose logs db

# Перезапустите сервисы
docker-compose restart
```

### Проблемы с миграциями
```bash
# Сброс миграций (ОСТОРОЖНО!)
docker-compose exec web python manage.py migrate --fake-initial

# Создание новых миграций
docker-compose exec web python manage.py makemigrations
```

### Очистка данных
```bash
# Остановка и удаление контейнеров
docker-compose down

# Удаление volumes (ВНИМАНИЕ: удалит все данные!)
docker-compose down -v

# Удаление образов
docker-compose down --rmi all
```

## Полезные команды

```bash
# Перезапуск конкретного сервиса
docker-compose restart web

# Просмотр использования ресурсов
docker-compose top

# Выполнение команд в контейнере
docker-compose exec web bash

# Просмотр конфигурации
docker-compose config
```

## Поддержка

При возникновении проблем:
1. Проверьте логи: `./docker-logs.sh`
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте доступность внешних сервисов (EIAS API, Mattermost)
