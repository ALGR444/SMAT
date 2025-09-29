# data_processor.py
import time
import threading
import random
from datetime import datetime
from database import db
from config import Config

class DataProcessor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_processing_time = 0

    def start_processing(self):
        """Запуск обработки данных в отдельном потоке"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._processing_loop)
        self.thread.daemon = True
        self.thread.start()
        print("DataProcessor: Фоновый обработчик запущен.")

    def stop_processing(self):
        """Остановка обработки данных"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("DataProcessor: Фоновый обработчик остановлен.")

    def _processing_loop(self):
        """Основной цикл обработки данных"""
        # Первоначальное заполнение базы тестовыми данными
        if not self._has_data():
            print("DataProcessor: База пуста. Заполняю тестовыми данными...")
            db.populate_test_data()

        while self.running:
            try:
                current_time = time.time()
                
                # Имитация периодической работы (раз в 10 секунд)
                if current_time - self.last_processing_time >= Config.REFRESH_INTERVAL:
                    self._process_new_data()      # Имитация получения новых свечей
                    self._process_order_blocks()  # Поиск и добавление новых блоков
                    self._update_confirmations()  # Обновление статусов подтверждения
                    self.last_processing_time = current_time
                
                time.sleep(1)  # Короткая пауза для снижения нагрузки
                
            except Exception as e:
                print(f"Ошибка в цикле обработки: {e}")
                time.sleep(5)

    def _has_data(self):
        """Проверяет, есть ли в базе данные"""
        blocks = db.get_order_blocks(limit=1)
        return len(blocks) > 0

    def _process_new_data(self):
        """Имитация получения новых свечных данных"""
        # С вероятностью 30% добавляем новую свечу
        if random.random() < 0.3:
            symbol = random.choice(Config.SYMBOLS)
            timeframe = random.choice(Config.TIMEFRAMES)
            
            # Получаем последнюю свечу для продолжения тренда
            latest_time = db.get_latest_candle_time(symbol, timeframe)
            latest_candles = db.get_candles_for_block_detection(symbol, timeframe, 1)
            
            if latest_candles:
                last_candle = latest_candles[0]
                new_time = latest_time + (int(timeframe) * 60000)
                
                # Создаем новую свечу на основе предыдущей
                new_candle = {
                    'open_time': new_time,
                    'open': last_candle['close'],
                    'high': last_candle['close'] * random.uniform(1.001, 1.02),
                    'low': last_candle['close'] * random.uniform(0.98, 0.999),
                    'close': last_candle['close'] * random.uniform(0.995, 1.005),
                    'volume': random.uniform(5000, 50000)
                }
                
                db.add_candle_data(symbol, timeframe, new_candle)
                print(f"DataProcessor: Добавлена новая свеча {symbol} {timeframe}")

    def _process_order_blocks(self):
        """Поиск и добавление новых ордер-блоков (имитация)"""
        # С вероятностью 20% находим новый блок
        if random.random() < 0.2:
            symbol = random.choice(Config.SYMBOLS)
            timeframe = random.choice(Config.TIMEFRAMES)
            block_type = random.choice(['bullish', 'bearish'])
            
            # Используем реальные данные из базы для реалистичности
            candles = db.get_candles_for_block_detection(symbol, timeframe, 10)
            if candles:
                # Выбираем случайный уровень цены из последних свечей
                price_level = random.choice([candle['high'] for candle in candles] + 
                                           [candle['low'] for candle in candles])
                
                # Временные метки для блока
                current_time = int(time.time() * 1000)
                open_time = current_time - random.randint(3600000, 7200000)
                close_time = open_time + random.randint(1800000, 3600000)
                
                # Добавляем новый блок (пока не подтвержденный)
                db.add_order_block(symbol, timeframe, block_type, price_level,
                                 open_time, close_time, confirmed=False)
                
                print(f"DataProcessor: Найден новый ордер-блок {symbol} {timeframe} {block_type}")

    def _update_confirmations(self):
        """Обновление статусов подтверждения ордер-блоков (имитация)"""
        # Получаем все неподтвержденные блоки
        all_blocks = db.get_order_blocks(limit=100)
        unconfirmed_blocks = [b for b in all_blocks if not b['confirmed']]
        
        # С вероятностью 25% подтверждаем случайный блок
        if unconfirmed_blocks and random.random() < 0.25:
            block_to_confirm = random.choice(unconfirmed_blocks)
            success = db.update_order_block_confirmation(block_to_confirm['id'], True)
            
            if success:
                print(f"DataProcessor: Ордер-блок {block_to_confirm['symbol']} подтвержден")

    def get_order_blocks(self):
        """Получение списка ордер-блоков из базы данных"""
        return db.get_order_blocks()

    def update_order_block_confirmation(self, block_id, confirmed):
        """Обновление статуса подтверждения ордер-блока"""
        return db.update_order_block_confirmation(block_id, confirmed)

# Глобальный экземпляр обработчика данных
data_processor = DataProcessor()
