import requests
import xml.etree.ElementTree as ET
from typing import Optional
from django.conf import settings
from django.utils import timezone
import logging
import re
from .models import UpdateLog, Template

logger = logging.getLogger(__name__)


class EIASAPIService:
    """Сервис для работы с API EIAS"""
    
    def __init__(self):
        self.base_url = settings.EIAS_API_BASE_URL
        self.timeout = 30
    
    def get_template_info(self, template: Template) -> Optional[UpdateLog]:
        """
        Получает информацию о шаблоне из API EIAS
        
        Args:
            template: Объект шаблона
            version: Версия шаблона для запроса
            
        Returns:
            Объект UpdateLog с информацией о шаблоне или None в случае ошибки
        """
        params = {
            'P_TC': template.template_code,
            'P_V': template.current_version,
            'P_NSRF': '',
            'P_ENTITY': '',
            'P_EXTENDED_INFO': ''
        }
        
        try:
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=self.timeout,
                verify=False  # ToDo: отключаем проверку SSL для отладки
            )
            response.raise_for_status()
            
            # Определяем кодировку и декодируем содержимое
            content = response.content
            xml_text = content.decode(response.encoding or 'utf-8') or None
            
            return self._parse_xml_response(xml_text, template)
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API EIAS для {template.template_code}: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Ошибка парсинга XML для {template.template_code}: {e}")
            return None
        except UnicodeDecodeError:
            logger.error(f"Ошибка декодирования XML для {template.template_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка для {template.template_code}: {e}")
            return None
    
    def _parse_xml_response(self, xml_text: str, template: Template) -> Optional[UpdateLog]:
        """
        Парсит XML ответ от API EIAS и создает объект UpdateLog
        
        Args:
            xml_text: XML текст ответа
            template: Объект шаблона
            
        Returns:
            Объект UpdateLog или None в случае ошибки
        """
        try:
            root = ET.fromstring(xml_text)
            # Сначала определяем namespace
            namespace = root.tag.split('}')[0][1:] if '}' in root.tag else ''
        
            # Проверяем изменения в проверках
            description_update = root.find(f'.//{{{namespace}}}DESCRIPTION_UPDATE').text
            if re.search( r'\bпровер\w*\b', description_update, re.IGNORECASE):
                has_validation_changes = True
            
            # Создаем объект UpdateLog
            update_log = UpdateLog(
                template=template,
                old_version=template.current_version,
                new_version=root.find(f'.//{{{namespace}}}VERSION').text,
                has_validation_changes=has_validation_changes,
                raw_xml=xml_text,
                message_status=UpdateLog.MessageStatus.NOTSENT
            )
            
            return update_log
            
        except ET.ParseError as e:
            logger.error(f"Ошибка парсинга XML для {template.template_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при парсинге XML для {template.template_code}: {e}")
            return None


class MattermostService:
    """Сервис для отправки уведомлений в Mattermost"""
    
    def __init__(self):
        self.webhook_url = settings.MATTERMOST_WEBHOOK_URL
        self.channel = settings.MATTERMOST_CHANNEL
    
    def send_template_update_notification(self, update_log: UpdateLog) -> bool:
        """
        Отправляет уведомление об обновлении шаблона
        
        Args:
            update_log: Объект UpdateLog с информацией об обновлении
            
        Returns:
            True если уведомление отправлено успешно, False иначе
        """
        if not self.webhook_url:
            logger.warning("Webhook URL для Mattermost не настроен")
            return False
        
        # Формируем сообщение
        emoji = "🚨" if update_log.has_validation_changes else "📝"
        title = f"{emoji} Обновление шаблона"
        
        message = f"**{title}**\n\n"
        message += f"**Шаблон:** `{update_log.template.template_code}`\n"
        message += f"**Версия:** `{update_log.old_version}` → `{update_log.new_version}`\n"
        
        if update_log.has_validation_changes:
            message += "⚠️ **КРИТИЧНОЕ ОБНОВЛЕНИЕ**\n"
            message += "🔍 **Изменения в проверках**\n"
        
        message += f"**Время:** {update_log.created_at.strftime('%d.%m.%Y %H:%M:%S')}"
        
        payload = {
            "text": message,
            "channel": self.channel,
            "username": "p4e_tpl_version_monitoring",
            "icon_emoji": ":robot_face:"
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Уведомление отправлено в Mattermost для {update_log.template.template_code}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Ошибка отправки уведомления в Mattermost: {e}")
            return False
