from django.db import models
from django.utils import timezone


class Template(models.Model):
    """Модель для хранения информации о шаблонах"""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        INACTIVE = 'inactive', 'Не активен'
    
    template_code = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Код шаблона"
    )
    current_version = models.CharField(
        max_length=50, 
        verbose_name="Текущая версия"
    )
    last_checked = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Последняя проверка"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Создан"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Обновлен"
    )

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"
        ordering = ['template_code']

    def __str__(self):
        return f"{self.template_code} (v{self.current_version})"


class UpdateLog(models.Model):
    """Лог поиска обновлений шаблонов"""
    
    class MessageStatus(models.TextChoices):
        SENT = 'SENT', 'Отправлено'
        NOTSENT = 'NOTSENT', 'Не отправлено'
        
    template = models.ForeignKey(
        Template, 
        on_delete=models.CASCADE, 
        verbose_name="Шаблон"
    )
    old_version = models.CharField(
        max_length=50, 
        verbose_name="Старая версия"
    )
    new_version = models.CharField(
        max_length=50, 
        verbose_name="Новая версия"
    )
    has_validation_changes = models.BooleanField(
        default=False, 
        verbose_name="Изменения в проверках"
    )
    message_status = models.CharField(
        max_length=10,
        choices=MessageStatus.choices,
        default=MessageStatus.NOTSENT,
        verbose_name="Статус сообщения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Создано"
    )
    raw_xml = models.TextField(
        blank=True,
        null=True,
        verbose_name="Исходный XML"
    )

    class Meta:
        verbose_name = "Лог обновления"
        verbose_name_plural = "Логи обновлений"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.template_code}: {self.old_version} → {self.new_version}"