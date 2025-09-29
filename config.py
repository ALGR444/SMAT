"""
Конфигурация проекта SMAT
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Класс конфигурации приложения"""
    
    # Bybit API
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
    
    # Настройки приложения
    DATA_DIR = os.getenv('DATA_DIR', './data')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Настройки API
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.2'))
    
    # Supported intervals
    SUPPORTED_INTERVALS = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        missing_configs = []
        
        if not cls.BYBIT_API_KEY:
            print("⚠️  BYBIT_API_KEY не установлен (необходим только для приватных методов)")
        
        if not cls.BYBIT_API_SECRET:
            print("⚠️  BYBIT_API_SECRET не установлен (необходим только для приватных методов)")
        
        # Создаем директорию для данных если не существует
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        
        print(f"✅ Директория для данных: {cls.DATA_DIR}")
        print(f"✅ Уровень логирования: {cls.LOG_LEVEL}")
        
        return len(missing_configs) == 0
