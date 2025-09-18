from django.contrib import admin
from .models import Template, UpdateLog


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        'template_code', 
        'current_version', 
        'last_checked', 
        'status'
    ]
    list_filter = ['status', 'last_checked']
    search_fields = ['template_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('template_code', 'current_version', 'status')
        }),
        ('Временные метки', {
            'fields': ('last_checked', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UpdateLog)
class UpdateLogAdmin(admin.ModelAdmin):
    list_display = [
        'template', 
        'old_version', 
        'new_version', 
        'has_validation_changes',
        'message_status',
        'created_at'
    ]
    list_filter = [ 
        'has_validation_changes', 
        'message_status', 
        'created_at'
    ]
    search_fields = ['template__template_code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация об обновлении', {
            'fields': (
                'template', 
                'old_version', 
                'new_version',
                'has_validation_changes'
            )
        }),
        ('Уведомления', {
            'fields': ('message_status',)
        }),
        ('Дополнительно', {
            'fields': ('raw_xml', 'created_at'),
            'classes': ('collapse',)
        }),
    )