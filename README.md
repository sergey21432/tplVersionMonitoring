# Система мониторинга обновлений шаблонов

Django приложение для автоматического мониторинга обновлений шаблонов через API EIAS с уведомлениями в Mattermost.

## Возможности

- ✅ Мониторинг шаблонов через API EIAS
- ✅ Автоматическое сравнение версий
- ✅ Уведомления в Mattermost
- ✅ Определение критичных обновлений
- ✅ Отслеживание изменений в проверках
- ✅ Логирование всех операций
- ✅ Django Admin интерфейс
- ✅ Management команды для управления

## Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE USER p4e_tpl_version_monitoring WITH PASSWORD '***';
CREATE SCHEMA p4e_tpl_version_monitoring 
    AUTHORIZATION p4e_tpl_version_monitoring;

GRANT ALL PRIVILEGES ON SCHEMA p4e_tpl_version_monitoring TO p4e_tpl_version_monitoring;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA p4e_tpl_version_monitoring TO p4e_tpl_version_monitoring;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA p4e_tpl_version_monitoring TO p4e_tpl_version_monitoring;

ALTER DEFAULT PRIVILEGES IN SCHEMA p4e_tpl_version_monitoring 
    GRANT ALL PRIVILEGES ON TABLES TO p4e_tpl_version_monitoring;
ALTER DEFAULT PRIVILEGES IN SCHEMA p4e_tpl_version_monitoring 
    GRANT ALL PRIVILEGES ON SEQUENCES TO p4e_tpl_version_monitoring;
```

### 3. Настройка переменных окружения

Скопируйте `config.env` в `.env` и настройте параметры:

```bash
cp config.env .env
```

Отредактируйте `.env`:

```env
# Database settings
DB_NAME=postgres
DB_USER=p4e_tpl_version_monitoring
DB_PASSWORD=***
DB_HOST=host
DB_PORT=5432

# Mattermost settings
MATTERMOST_WEBHOOK_URL=https://your-mattermost-server.com/hooks/your-webhook-id
MATTERMOST_CHANNEL=template-updates

# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
```

### 4. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
py manage.py createsuperuser
```

### 6. Создание директории для логов

```bash
mkdir logs
```

## Использование

### Management команды

#### Проверка обновлений шаблонов

```bash
# Проверить все активные шаблоны
python manage.py check_template_updates

# Проверить конкретный шаблон
python manage.py check_template_updates --template-code FORM.1.TSO.2026.ORG

# Тестовый запуск без отправки уведомлений
python manage.py check_template_updates --dry-run
```

#### Добавление шаблона

```bash
# Добавить новый шаблон
python manage.py add_template FORM.1.TSO.2026.ORG --version 1.0.6

# Добавить неактивный шаблон
python manage.py add_template FORM.2.TSO.2026.ORG --status inactive
```

#### Тестирование API

```bash
# Тест API EIAS
python manage.py test_eias_api FORM.1.TSO.2026.ORG --version 1.0.6 --show-xml

# Тест Mattermost
python manage.py test_mattermost --template-code TEST.TEMPLATE --critical
```

### Настройка cron

Добавьте в crontab для автоматической проверки:

```bash
# Каждый час
0 * * * * cd /path/to/project && python manage.py check_template_updates

# Каждые 30 минут в рабочее время
*/30 9-18 * * 1-5 cd /path/to/project && python manage.py check_template_updates
```

### Django Admin

Запустите сервер разработки:

```bash
python manage.py runserver
```

Откройте http://127.0.0.1:8000/admin/ для управления шаблонами и просмотра логов.

## Структура проекта

```
tplVersionMonitoring/
├── templates/                    # Django приложение
│   ├── management/
│   │   └── commands/            # Management команды
│   │       ├── check_template_updates.py
│   │       ├── add_template.py
│   │       ├── test_eias_api.py
│   │       └── test_mattermost.py
│   ├── models.py               # Модели данных
│   ├── admin.py                # Админ интерфейс
│   └── services.py             # Сервисы для API и уведомлений
├── tplVersionMonitoring/
│   ├── settings.py             # Настройки Django
│   └── urls.py
├── requirements.txt            # Зависимости Python
├── config.env                 # Пример конфигурации
├── crontab.txt               # Примеры cron задач
└── README.md                 # Документация
```

## Модели данных

### Template

- `template_code` - Код шаблона
- `current_version` - Текущая версия
- `status` - Статус (активен/неактивен)
- `last_checked` - Время последней проверки

### UpdateLog

- `template` - Ссылка на шаблон
- `old_version` - Старая версия
- `new_version` - Новая версия
- `has_validation_changes` - Изменения в проверках
- `message_status` - Статус уведомления
- `raw_xml` - Исходный XML ответ

## API EIAS

Приложение делает GET запросы к:

```
https://eias.ru/procwsxls/GET_UPDATE_INFO?P_TC={template_code}&P_V={version}&P_NSRF=&P_ENTITY=&P_EXTENDED_INFO=
```

## Уведомления Mattermost

Уведомления отправляются через webhook с информацией:

- Код шаблона
- Старая и новая версии
- Критичность обновления
- Изменения в проверках
- Время обновления

## Логирование

Логи сохраняются в `logs/template_monitor.log` и включают:

- Информацию о запросах к API
- Результаты проверки версий
- Статус отправки уведомлений
- Ошибки и исключения

## Устранение неполадок

### Ошибки подключения к базе данных

- Проверьте настройки в `.env`
- Убедитесь, что PostgreSQL запущен
- Проверьте права пользователя

### Ошибки API EIAS

- Проверьте доступность https://eias.ru
- Убедитесь в корректности кода шаблона
- Проверьте логи для детальной информации

### Проблемы с Mattermost

- Проверьте webhook URL
- Убедитесь в корректности канала
- Проверьте права webhook'а

## Разработка

### Добавление новых полей

1. Измените модели в `models.py`
2. Создайте миграцию: `python manage.py makemigrations`
3. Примените миграцию: `python manage.py migrate`

### Расширение функциональности

- Добавьте новые методы в `services.py`
- Создайте новые management команды
- Обновите admin интерфейс при необходимости
