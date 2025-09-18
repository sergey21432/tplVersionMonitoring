from django.core.management.base import BaseCommand
from templates.services import EIASAPIService
import json


class Command(BaseCommand):
    help = 'Тестирует подключение к API EIAS и парсинг XML ответов'

    def add_arguments(self, parser):
        parser.add_argument(
            'template_code',
            type=str,
            help='Код шаблона для тестирования'
        )
        parser.add_argument(
            '--version',
            type=str,
            default='1.0.0',
            help='Версия шаблона для запроса'
        )
        parser.add_argument(
            '--show-xml',
            action='store_true',
            help='Показать полный XML ответ'
        )

    def handle(self, *args, **options):
        template_code = options['template_code']
        version = options['version']
        
        self.stdout.write(f'Тестируем API EIAS для шаблона: {template_code}')
        self.stdout.write(f'Версия: {version}')
        self.stdout.write('-' * 50)
        
        # Инициализируем сервис
        eias_service = EIASAPIService()
        
        # Выполняем запрос
        self.stdout.write('Отправляем запрос к API...')
        api_data = eias_service.get_template_info(template_code, version)
        
        if not api_data:
            self.stdout.write(
                self.style.ERROR('Не удалось получить данные от API')
            )
            return
        
        # Выводим результаты
        self.stdout.write(
            self.style.SUCCESS('Данные успешно получены!')
        )
        
        self.stdout.write(f'Код шаблона: {api_data.get("template_code")}')
        self.stdout.write(f'Последняя версия: {api_data.get("latest_version")}')
        self.stdout.write(f'Изменения в проверках: {api_data.get("has_validation_changes")}')
        self.stdout.write(f'Время парсинга: {api_data.get("parsed_at")}')
        
        if options['show_xml'] and api_data.get('raw_xml'):
            self.stdout.write('\n' + '='*50)
            self.stdout.write('XML ОТВЕТ:')
            self.stdout.write('='*50)
            self.stdout.write(api_data['raw_xml'])
        
        # Показываем структуру данных
        self.stdout.write('\n' + '='*50)
        self.stdout.write('СТРУКТУРА ДАННЫХ:')
        self.stdout.write('='*50)
        
        for key, value in api_data.items():
            if key != 'raw_xml':  # Пропускаем XML для краткости
                self.stdout.write(f'{key}: {value}')
