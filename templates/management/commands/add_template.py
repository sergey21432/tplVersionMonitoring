from django.core.management.base import BaseCommand
from templates.models import Template


class Command(BaseCommand):
    help = 'Добавляет новый шаблон в базу данных для мониторинга'

    def add_arguments(self, parser):
        parser.add_argument(
            'template_code',
            type=str,
            help='Код шаблона (например: FORM.1.TSO.2026.ORG)'
        )
        parser.add_argument(
            '--version',
            type=str,
            default='1.0.0',
            help='Начальная версия шаблона (по умолчанию: 1.0.0)'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['active', 'inactive'],
            default='active',
            help='Статус шаблона (по умолчанию: active)'
        )

    def handle(self, *args, **options):
        template_code = options['template_code']
        version = options['version']
        status = options['status']
        
        # Проверяем, не существует ли уже такой шаблон
        if Template.objects.filter(template_code=template_code).exists():
            self.stdout.write(
                self.style.ERROR(f'Шаблон {template_code} уже существует в базе данных')
            )
            return
        
        # Создаем новый шаблон
        template = Template.objects.create(
            template_code=template_code,
            current_version=version,
            status=status
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Шаблон {template_code} успешно добавлен с версией {version} и статусом {status}'
            )
        )
        
        # Показываем информацию о созданном шаблоне
        self.stdout.write(f'ID: {template.id}')
        self.stdout.write(f'Код: {template.template_code}')
        self.stdout.write(f'Версия: {template.current_version}')
        self.stdout.write(f'Статус: {template.get_status_display()}')
        self.stdout.write(f'Создан: {template.created_at}')
