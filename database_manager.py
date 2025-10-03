# database_manager.py
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, desc
from models import DatabaseManager, KlineData, Symbol
import pandas as pd

class DataManager:
    def __init__(self, db_path="data/smat.db"):
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_database()
        self.logger = logging.getLogger(__name__)
    
    def store_klines(self, symbol, timeframe, klines_data):
        """Сохранить данные свечей в базу данных"""
        session = self.db_manager.get_session()
        try:
            added_count = 0
            updated_count = 0
            
            for kline in klines_data:
                # Проверяем, существует ли уже запись
                existing = session.query(KlineData).filter(
                    and_(
                        KlineData.symbol == symbol,
                        KlineData.timeframe == timeframe,
                        KlineData.timestamp == kline['timestamp']
                    )
                ).first()
                
                if existing:
                    # Обновляем существующую запись
                    existing.open = kline['open']
                    existing.high = kline['high']
                    existing.low = kline['low']
                    existing.close = kline['close']
                    existing.volume = kline['volume']
                    existing.turnover = kline.get('turnover')
                    updated_count += 1
                else:
                    # Создаем новую запись
                    new_kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        timestamp=kline['timestamp'],
                        open=kline['open'],
                        high=kline['high'],
                        low=kline['low'],
                        close=kline['close'],
                        volume=kline['volume'],
                        turnover=kline.get('turnover')
                    )
                    session.add(new_kline)
                    added_count += 1
            
            session.commit()
            self.logger.info(f"Символ {symbol} ({timeframe}): добавлено {added_count}, обновлено {updated_count}")
            return added_count + updated_count
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Ошибка сохранения данных для {symbol}: {e}")
            raise
        finally:
            session.close()
    
    def get_klines(self, symbol, timeframe, start_time=None, end_time=None, limit=1000):
        """Получить данные свечей из базы данных"""
        session = self.db_manager.get_session()
        try:
            query = session.query(KlineData).filter(
                and_(
                    KlineData.symbol == symbol,
                    KlineData.timeframe == timeframe
                )
            )
            
            if start_time:
                query = query.filter(KlineData.timestamp >= start_time)
            if end_time:
                query = query.filter(KlineData.timestamp <= end_time)
            
            query = query.order_by(KlineData.timestamp).limit(limit)
            results = query.all()
            
            data = []
            for row in results:
                data.append({
                    'timestamp': row.timestamp,
                    'open': row.open,
                    'high': row.high,
                    'low': row.low,
                    'close': row.close,
                    'volume': row.volume,
                    'turnover': row.turnover
                })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Ошибка получения данных для {symbol}: {e}")
            return []
        finally:
            session.close()
    
    def get_klines_df(self, symbol, timeframe, start_time=None, end_time=None, limit=1000):
        """Получить данные в формате pandas DataFrame"""
        data = self.get_klines(symbol, timeframe, start_time, end_time, limit)
        if data:
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            return df
        return pd.DataFrame()
    
    def get_last_timestamp(self, symbol, timeframe):
        """Получить временную метку последней доступной свечи"""
        session = self.db_manager.get_session()
        try:
            last_kline = session.query(KlineData).filter(
                and_(
                    KlineData.symbol == symbol,
                    KlineData.timeframe == timeframe
                )
            ).order_by(desc(KlineData.timestamp)).first()
            
            return last_kline.timestamp if last_kline else None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения последней временной метки для {symbol}: {e}")
            return None
        finally:
            session.close()
    
    def get_available_symbols(self):
        """Получить список доступных символов"""
        session = self.db_manager.get_session()
        try:
            symbols = session.query(Symbol).filter(Symbol.is_active == True).all()
            return [s.symbol for s in symbols]
        except Exception as e:
            self.logger.error(f"Ошибка получения списка символов: {e}")
            return []
        finally:
            session.close()
    
    def update_symbols_from_bybit(self, bybit_api):
        """Обновить список символов из Bybit API"""
        try:
            symbols_info = bybit_api.get_symbols_info()
            symbols_list = []
            
            for symbol in symbols_info:
                symbols_list.append({
                    'symbol': symbol,
                    'base_currency': symbol.replace('USDT', ''),
                    'quote_currency': 'USDT'
                })
            
            self.db_manager.add_symbols(symbols_list)
            self.logger.info(f"Обновлено {len(symbols_list)} символов из Bybit")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления символов из Bybit: {e}")
            raise