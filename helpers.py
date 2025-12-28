"""
Утилиты и функции помощники
"""
import logging
import psutil
import json
from datetime import datetime
import os

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"raven_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('RavenAI')

def log_activity(action, details=""):
    """Логирование активности"""
    try:
        if isinstance(details, dict):
            details = json.dumps(details, ensure_ascii=False)
        logger.info(f"{action}: {details}")
    except:
        logger.info(f"{action}: {str(details)[:100]}")

def get_system_status():
    """Получить статус системы"""
    try:
        return {
            'cpu': psutil.cpu_percent(interval=0.5),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('C:\\').percent if os.name == 'nt' else psutil.disk_usage('/').percent,
            'processes': len(psutil.pids()),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса системы: {e}")
        return {'error': str(e)}

def load_config(config_path):
    """Загрузка конфигурационного файла"""
    default_config = {}
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки конфига {config_path}: {e}")
    
    return default_config

def save_config(config_path, config):
    """Сохранение конфигурационного файла"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения конфига {config_path}: {e}")
        return False