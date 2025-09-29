# database.py
import sqlite3
import random
import time
from datetime import datetime
from config import Config

class Database:
    def __init__(self, db_name='smat.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица для хранения данных свечей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candle_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            open_time INTEGER NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL,
            UNIQUE(symbol, timeframe, open_time)
        )
        ''')

        # Таблица для хранения найденных ордер-блоков
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            block_type TEXT NOT NULL,
            price_level REAL NOT NULL,
            open_time INTEGER NOT NULL,
            close_time INTEGER NOT NULL,
            confirmed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def add_candle_data(self, symbol, timeframe, candle_data):
        """Добавление данных свечи в базу"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO candle_data
            (symbol, timeframe, open_time, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, timeframe, candle_data['open_time'],
                  candle_data['open'], candle_data['high'],
                  candle_data['low'], candle_data['close'],
                  candle_data['volume']))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении данных свечи: {e}")
        finally:
            conn.close()

    def add_order_block(self, symbol, timeframe, block_type, price_level, open_time, close_time, confirmed=False):
        """Добавление найденного ордер-блока"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO order_blocks
            (symbol, timeframe, block_type, price_level, open_time, close_time, confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, timeframe, block_type, price_level, open_time, close_time, confirmed))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении ордер-блока: {e}")
        finally:
            conn.close()

    def get_order_blocks(self, limit=100):
        """Получение списка ордер-блоков"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT id, symbol, timeframe, block_type, price_level,
                   open_time, close_time, confirmed, created_at
            FROM order_blocks
            ORDER BY created_at DESC
            LIMIT ?
            ''', (limit,))
            
            blocks = []
            for row in cursor.fetchall():
                blocks.append({
                    'id': row[0],
                    'symbol': row[1],
                    'timeframe': row[2],
                    'block_type': row[3],
                    'price_level': row[4],
                    'open_time': row[5],
                    'close_time': row[6],
                    'confirmed': bool(row[7]),
                    'created_at': row[8]
                })
            return blocks
        except Exception as e:
            print(f"Ошибка при получении ордер-блоков: {e}")
            return []
        finally:
            conn.close()

    def get_latest_candle_time(self, symbol, timeframe):
        """Получение времени последней свечи для пары и таймфрейма"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT MAX(open_time) FROM candle_data
            WHERE symbol = ? AND timeframe = ?
            ''', (symbol, timeframe))
            result = cursor.fetchone()
            return result[0] if result[0] else None
        except Exception as e:
            print(f"Ошибка при получении времени последней свечи: {e}")
            return None
        finally:
            conn.close()

    def get_candles_for_block_detection(self, symbol, timeframe, limit=50):
        """Получение свечей для анализа ордер-блоков"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT open_time, open, high, low, close, volume
            FROM candle_data
            WHERE symbol = ? AND timeframe = ?
            ORDER BY open_time DESC
            LIMIT ?
            ''', (symbol, timeframe, limit))
            
            candles = []
            for row in cursor.fetchall():
                candles.append({
                    'open_time': row[0],
                    'open': row[1],
                    'high': row[2],
                    'low': row[3],
                    'close': row[4],
                    'volume': row[5]
                })
            return candles
        except Exception as e:
            print(f"Ошибка при получении свечей для анализа: {e}")
            return []
        finally:
            conn.close()

    def update_order_block_confirmation(self, block_id, confirmed):
        """Обновление статуса подтверждения ордер-блока"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE order_blocks SET confirmed = ? WHERE id = ?
            ''', (confirmed, block_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении статуса ордер-блока: {e}")
            return False
        finally:
            conn.close()

    def populate_test_data(self):
        """Заполнение базы тестовыми данными"""
        symbols = Config.SYMBOLS
        timeframes = Config.TIMEFRAMES
        current_time = int(time.time() * 1000)
        
        print("Database: Заполнение тестовыми данными...")
        
        # Генерация тестовых свечных данных
        for symbol in symbols:
            for timeframe in timeframes:
                # Создаем реалистичный ценовой тренд для каждого символа
                base_price = random.uniform(1000, 50000)
                price_trend = base_price
                
                for i in range(200):  # 200 свечей на каждый таймфрейм
                    candle_time = current_time - ((199 - i) * int(timeframe) * 60000)
                    
                    # Создаем тренд (+/- 10% от базовой цены)
                    price_trend += random.uniform(-0.1, 0.1) * base_price
                    
                    candle_data = {
                        'open_time': candle_time,
                        'open': price_trend,
                        'high': price_trend * random.uniform(1.001, 1.03),
                        'low': price_trend * random.uniform(0.97, 0.999),
                        'close': price_trend * random.uniform(0.99, 1.01),
                        'volume': random.uniform(1000, 100000)
                    }
                    self.add_candle_data(symbol, timeframe, candle_data)

        # Генерация тестовых ордер-блоков
        for i in range(25):
            symbol = random.choice(symbols)
            timeframe = random.choice(timeframes)
            block_type = random.choice(['bullish', 'bearish'])
            
            # Получаем реальные ценовые уровни из существующих свечей
            candles = self.get_candles_for_block_detection(symbol, timeframe, 20)
            if candles:
                price_level = random.choice([candle['high'] for candle in candles] + 
                                           [candle['low'] for candle in candles])
                
                open_time = current_time - random.randint(3600000, 86400000)
                close_time = open_time + random.randint(300000, 3600000)
                confirmed = random.choice([True, False])
                
                self.add_order_block(symbol, timeframe, block_type, price_level,
                                   open_time, close_time, confirmed)
        
        print("Database: Тестовые данные успешно добавлены!")

# Создаем глобальный экземпляр базы данных
db = Database()
