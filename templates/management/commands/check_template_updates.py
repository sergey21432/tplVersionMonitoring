from django.core.management.base import BaseCommand
from django.utils import timezone
from templates.models import Template, UpdateLog
from templates.services import EIASAPIService, MattermostService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Проверяет обновления шаблонов через API EIAS и отправляет уведомления в Mattermost'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template-code',
            type=str,
            help='Проверить конкретный шаблон по коду'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Запустить в режиме тестирования без отправки уведомлений'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Запустить в режиме отладки с debugpy сервером'
        )

    def handle(self, *args, **options):
        # Настройка отладки
        if options['debug']:
            import debugpy
            debugpy.listen(("localhost", 5678))
            self.stdout.write(
                self.style.WARNING('🐛 Debugger запущен на порту 5678. Подключитесь из VS Code...')
            )
            self.stdout.write(
                self.style.WARNING('⏳ Ожидание подключения отладчика...')
            )
            debugpy.wait_for_client()
            self.stdout.write(
                self.style.SUCCESS('✅ Отладчик подключен!')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Начинаем проверку обновлений шаблонов...')
        )
        
        # Инициализируем сервисы
        eias_service = EIASAPIService()
        mattermost_service = MattermostService()
        
        # Получаем шаблоны для проверки
        if options['template_code']:
            templates = Template.objects.filter(
                template_code=options['template_code'],
                status=Template.Status.ACTIVE
            )
        else:
            templates = Template.objects.filter(status=Template.Status.ACTIVE)
        
        if not templates.exists():
            self.stdout.write(
                self.style.WARNING('Не найдено активных шаблонов для проверки')
            )
            return
        
        self.stdout.write(f'Найдено {templates.count()} шаблонов для проверки')
        
        updated_count = 0
        error_count = 0
        
        for template in templates:
            try:
                self.stdout.write(f'Проверяем шаблон: {template.template_code}')
                
                # Получаем информацию о шаблоне из API
                update_log = eias_service.get_template_info(template)
                if not update_log:
                    self.stdout.write(
                        self.style.ERROR(f'Не удалось получить данные для {template.template_code}')
                    )
                    error_count += 1
                    continue
                
                # Проверяем, изменилась ли версия
                if update_log.new_version == template.current_version:
                    self.stdout.write(
                        f'Версия актуальна: {template.template_code} ({update_log.new_version})'
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Обнаружено обновление: {template.template_code} '
                            f'{template.current_version} → {update_log.new_version}'
                        )
                    )
                    
                    # Сохраняем запись в логе только при обновлении
                    update_log.save()
                    
                    # Отправляем уведомление в Mattermost (если не dry-run)
                    if not options['dry_run']:
                        success = mattermost_service.send_template_update_notification(update_log)
                        
                        if success:
                            update_log.message_status = UpdateLog.MessageStatus.SENT
                            update_log.save()
                            # Обновляем версию в базе данных
                            template.current_version = update_log.new_version
                            self.stdout.write(
                                self.style.SUCCESS(f'Уведомление отправлено для {template.template_code}')
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'Ошибка отправки уведомления для {template.template_code}')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'[DRY RUN] Уведомление НЕ отправлено для {template.template_code}')
                        )
                    updated_count += 1
                    
                # Обновляем время последней проверки
                template.last_checked = timezone.now()
                template.save()
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при обработке {template.template_code}: {e}')
                )
                error_count += 1
                logger.error(f'Ошибка при обработке шаблона {template.template_code}: {e}')
        
        # Выводим итоговую статистику
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Проверка завершена!')
        )
        self.stdout.write(f'Обновлено шаблонов: {updated_count}')
        self.stdout.write(f'Ошибок: {error_count}')
        self.stdout.write(f'Всего проверено: {templates.count()}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('Запуск в режиме DRY RUN - уведомления не отправлялись')
            )
