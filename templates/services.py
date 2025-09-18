import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone
import logging
import re

logger = logging.getLogger(__name__)


class EIASAPIService:
    """Сервис для работы с API EIAS"""
    
    def __init__(self):
        self.base_url = settings.EIAS_API_BASE_URL
        self.timeout = 30
    
    def get_template_info(self, template_code: str, version: str = "1.0.0") -> Optional[Dict]:
        """
        Получает информацию о шаблоне из API EIAS
        
        Args:
            template_code: Код шаблона
            version: Версия шаблона для запроса
            
        Returns:
            Словарь с информацией о шаблоне или None в случае ошибки
        """
        params = {
            'P_TC': template_code,
            'P_V': version,
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
            
            return self._parse_xml_response(xml_text, template_code)
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API EIAS для {template_code}: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Ошибка парсинга XML для {template_code}: {e}")
            return None
        except UnicodeDecodeError:
            logger.error(f"Ошибка декодирования XML для {template_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка для {template_code}: {e}")
            return None
    
    def _parse_xml_response(self, xml_text: str, template_code: str) -> Dict:
        """
        Парсит XML ответ от API EIAS
        
        Args:
            root: Корневой элемент XML
            template_code: Код шаблона
            
        Returns:
            Словарь с извлеченной информацией
        """
        result = {
            'template_code': template_code,
            'latest_version': None,
            'has_validation_changes': False,
            'raw_xml': xml_text,
            'parsed_at': timezone.now()
        }
        
        root = ET.fromstring(xml_text)
        # Сначала определяем namespace
        namespace = root.tag.split('}')[0][1:] if '}' in root.tag else ''
        # Ищем информацию о версии
        result['latest_version'] = root.find(f'.//{{{namespace}}}VERSION').text
        
        # Проверяем изменения в проверках
        description_update = root.find(f'.//{{{namespace}}}DESCRIPTION_UPDATE').text
        if re.search( r'\bпровер\w*\b', description_update, re.IGNORECASE):
            result['has_validation_changes'] = True
        
        return result


class MattermostService:
    """Сервис для отправки уведомлений в Mattermost"""
    
    def __init__(self):
        self.webhook_url = settings.MATTERMOST_WEBHOOK_URL
        self.channel = settings.MATTERMOST_CHANNEL
    
    def send_template_update_notification(
        self, 
        template_code: str, 
        old_version: str, 
        new_version: str,
        has_validation_changes: bool = False
    ) -> bool:
        """
        Отправляет уведомление об обновлении шаблона
        
        Args:
            template_code: Код шаблона
            old_version: Старая версия
            new_version: Новая версия
            has_validation_changes: Есть ли изменения в проверках
            
        Returns:
            True если уведомление отправлено успешно, False иначе
        """
        if not self.webhook_url:
            logger.warning("Webhook URL для Mattermost не настроен")
            return False
        
        # Формируем сообщение
        emoji = "🚨" if has_validation_changes else "📝"
        title = f"{emoji} Обновление шаблона"
        
        message = f"**{title}**\n\n"
        message += f"**Шаблон:** `{template_code}`\n"
        message += f"**Версия:** `{old_version}` → `{new_version}`\n"
        
        if has_validation_changes:
            message += "⚠️ **КРИТИЧНОЕ ОБНОВЛЕНИЕ**\n"
            message += "🔍 **Изменения в проверках**\n"
        
        message += f"**Время:** {timezone.now().strftime('%d.%m.%Y %H:%M:%S')}"
        
        payload = {
            "text": message,
            "channel": self.channel,
            "username": "Template Monitor",
            "icon_emoji": ":robot_face:"
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Уведомление отправлено в Mattermost для {template_code}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Ошибка отправки уведомления в Mattermost: {e}")
            return False
