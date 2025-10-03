# data_collector.py
import logging
from datetime import datetime, timedelta
from database_manager import DataManager
from bybit_api import BybitAPI

class DataCollector:
    def __init__(self, db_path="data/smat.db"):
        self.data_manager = DataManager(db_path)
        self.bybit_api = BybitAPI()
        self.logger = logging.getLogger(__name__)
    
    def initialize_symbols(self):
        """Инициализировать список символов"""
        self.logger.info("Инициализация списка символов...")
        self.data_manager.update_symbols_from_bybit(self.bybit_api)
    
    def collect_historical_data(self, symbol, timeframe, days_back=30):
        """Собрать исторические данные за указанный период"""
        self.logger.info(f"Сбор исторических данных для {symbol} ({timeframe}) за {days_back} дней")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Проверяем последние доступные данные
        last_timestamp = self.data_manager.get_last_timestamp(symbol, timeframe)
        if last_timestamp:
            start_time = max(start_time, last_timestamp + timedelta(minutes=1))
        
        if start_time >= end_time:
            self.logger.info(f"Данные для {symbol} уже актуальны")
            return
        
        klines = self.bybit_api.get_multiple_klines(symbol, timeframe, start_time, end_time)
        
        if klines:
            stored_count = self.data_manager.store_klines(symbol, timeframe, klines)
            self.logger.info(f"Сохранено {stored_count} свечей для {symbol}")
        else:
            self.logger.warning(f"Не удалось получить данные для {symbol}")
    
    def collect_multiple_symbols(self, symbols, timeframe, days_back=30):
        """Собрать данные для нескольких символов"""
        for symbol in symbols:
            try:
                self.collect_historical_data(symbol, timeframe, days_back)
            except Exception as e:
                self.logger.error(f"Ошибка сбора данных для {symbol}: {e}")
    
    def update_all_data(self, timeframe='15', days_back=1):
        """Обновить все данные для активных символов"""
        symbols = self.data_manager.get_available_symbols()
        self.logger.info(f"Обновление данных для {len(symbols)} символов")
        self.collect_multiple_symbols(symbols, timeframe, days_back)