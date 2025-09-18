from django.core.management.base import BaseCommand
from templates.services import MattermostService


class Command(BaseCommand):
    help = 'Тестирует отправку уведомлений в Mattermost'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template-code',
            type=str,
            default='TEST.TEMPLATE.001',
            help='Код шаблона для тестового сообщения'
        )
        parser.add_argument(
            '--old-version',
            type=str,
            default='1.0.0',
            help='Старая версия'
        )
        parser.add_argument(
            '--new-version',
            type=str,
            default='1.0.1',
            help='Новая версия'
        )
        parser.add_argument(
            '--critical',
            action='store_true',
            help='Отправить как критичное обновление'
        )
        parser.add_argument(
            '--validation-changes',
            action='store_true',
            help='Указать изменения в проверках'
        )

    def handle(self, *args, **options):
        template_code = options['template_code']
        old_version = options['old_version']
        new_version = options['new_version']
        is_critical = options['critical']
        has_validation_changes = options['validation_changes']
        
        self.stdout.write('Тестируем отправку уведомления в Mattermost...')
        self.stdout.write('-' * 50)
        
        # Инициализируем сервис
        mattermost_service = MattermostService()
        
        # Проверяем настройки
        if not mattermost_service.webhook_url:
            self.stdout.write(
                self.style.ERROR('Webhook URL для Mattermost не настроен!')
            )
            self.stdout.write('Установите MATTERMOST_WEBHOOK_URL в настройках')
            return
        
        if not mattermost_service.channel:
            self.stdout.write(
                self.style.WARNING('Канал для Mattermost не настроен!')
            )
            self.stdout.write('Установите MATTERMOST_CHANNEL в настройках')
        
        # Показываем параметры тестового сообщения
        self.stdout.write(f'Шаблон: {template_code}')
        self.stdout.write(f'Версия: {old_version} → {new_version}')
        self.stdout.write(f'Критичное: {is_critical}')
        self.stdout.write(f'Изменения в проверках: {has_validation_changes}')
        self.stdout.write(f'Webhook URL: {mattermost_service.webhook_url}')
        self.stdout.write(f'Канал: {mattermost_service.channel}')
        
        # Отправляем тестовое уведомление
        self.stdout.write('\nОтправляем тестовое уведомление...')
        
        success = mattermost_service.send_template_update_notification(
            template_code=template_code,
            old_version=old_version,
            new_version=new_version,
            has_validation_changes=has_validation_changes
        )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('Тестовое уведомление успешно отправлено!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Ошибка отправки тестового уведомления!')
            )
            self.stdout.write('Проверьте настройки Mattermost и логи приложения')
