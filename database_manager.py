import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "data/smat.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц если их нет"""
        try:
            # Создаем директорию если её нет
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            
        except sqlite3.Error as e:
            print(f"Ошибка инициализации базы данных: {e}")
            raise

    # МЕТОДЫ ДЛЯ GUI
    
    def get_unique_symbols(self) -> List[str]:
        """Получение уникальных символов из БД"""
        try:
            self.cursor.execute("SELECT DISTINCT symbol FROM order_blocks ORDER BY symbol")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting unique symbols: {e}")
            return []

    def get_unique_timeframes(self) -> List[str]:
        """Получение уникальных таймфреймов из БД"""
        try:
            self.cursor.execute("SELECT DISTINCT timeframe FROM order_blocks ORDER BY timeframe")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting unique timeframes: {e}")
            return []

    def get_order_blocks(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> List[Tuple]:
        """Получение ордер-блоков с фильтрацией - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Используем реальные названия колонок из вашей таблицы
            query = """
            SELECT id, symbol, timeframe, direction, confirmation_strength, 
                   imbalance_high, is_confirmed, timestamp 
            FROM order_blocks 
            WHERE 1=1
            """
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if timeframe:
                query += " AND timeframe = ?"
                params.append(timeframe)
                
            query += " ORDER BY timestamp DESC"
            
            print(f"Executing query: {query}")
            self.cursor.execute(query, params)
            blocks = self.cursor.fetchall()
            print(f"Found {len(blocks)} blocks in database")
            return blocks
            
        except sqlite3.Error as e:
            print(f"Error getting order blocks: {e}")
            return []

    def add_test_order_blocks(self):
        """Добавление тестовых данных для демонстрации - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Используем реальную структуру таблицы
            test_blocks = [
                ('BTCUSDT', '1h', 'up', 0.8, 45000.0, 1, '2024-01-15 10:00:00'),
                ('ETHUSDT', '4h', 'down', 0.6, 2500.0, 1, '2024-01-15 12:00:00'),
                ('BTCUSDT', '1d', 'up', 0.9, 42000.0, 0, '2024-01-14 08:00:00'),
                ('ADAUSDT', '1h', 'down', 0.7, 0.45, 1, '2024-01-15 14:00:00'),
            ]
            
            for block in test_blocks:
                symbol, timeframe, direction, confirmation_strength, imbalance_high, is_confirmed, timestamp = block
                
                self.cursor.execute(
                    """INSERT OR IGNORE INTO order_blocks 
                    (symbol, timeframe, direction, confirmation_strength, imbalance_high, is_confirmed, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (symbol, timeframe, direction, confirmation_strength, imbalance_high, is_confirmed, timestamp)
                )
            
            self.connection.commit()
            print("Added test order blocks")
            
        except sqlite3.Error as e:
            print(f"Error adding test data: {e}")

    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
