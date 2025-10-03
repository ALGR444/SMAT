# block_processor.py
import logging
from datetime import datetime
from database_manager import DataManager
from order_block_detector import OrderBlockDetector
from models import OrderBlock

class BlockProcessor:
    def __init__(self, db_path="data/smat.db"):
        self.data_manager = DataManager(db_path)
        self.detector = OrderBlockDetector()
        self.logger = logging.getLogger(__name__)
    
    def find_blocks_all_symbols(self, timeframes=None):
        """
        Поиск ордер-блоков по всем символам и таймфреймам
        """
        if timeframes is None:
            timeframes = ['5', '15', '60', '240', 'D']
        
        symbols = self.data_manager.get_available_symbols()
        self.logger.info(f"Начинаем поиск ордер-блоков для {len(symbols)} символов")
        
        all_blocks = []
        
        for symbol in symbols:
            try:
                blocks = self.find_blocks_for_symbol(symbol, timeframes)
                all_blocks.extend(blocks)
                self.logger.info(f"Символ {symbol}: найдено {len(blocks)} блоков")
            except Exception as e:
                self.logger.error(f"Ошибка обработки символа {symbol}: {e}")
        
        # Сохраняем найденные блоки в БД
        self._save_blocks_to_db(all_blocks)
        return all_blocks
    
    def find_blocks_for_symbol(self, symbol: str, timeframes: list):
        """
        Поиск ордер-блоков для конкретного символа
        """
        blocks = []
        
        for timeframe in timeframes:
            try:
                # Получаем данные из БД
                df = self.data_manager.get_klines_df(symbol, timeframe, limit=1000)
                if df.empty:
                    continue
                
                # Ищем ордер-блоки
                symbol_blocks = self.detector.find_order_blocks(df, timeframe)
                
                # Добавляем информацию о символе
                for block in symbol_blocks:
                    block['symbol'] = symbol
                    blocks.append(block)
                    
            except Exception as e:
                self.logger.error(f"Ошибка обработки {symbol} ({timeframe}): {e}")
        
        return blocks
    
    def _save_blocks_to_db(self, blocks: list):
        """
        Сохранение найденных ордер-блоков в базу данных
        """
        session = self.data_manager.db_manager.get_session()
        try:
            # Очищаем старые неподтвержденные блоки
            session.query(OrderBlock).filter(OrderBlock.is_confirmed == False).delete()
            
            # Добавляем новые блоки
            for block_data in blocks:
                block = OrderBlock(**block_data)
                session.add(block)
            
            session.commit()
            self.logger.info(f"Сохранено {len(blocks)} ордер-блоков в БД")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Ошибка сохранения ордер-блоков: {e}")
            raise
        finally:
            session.close()
    
    def get_confirmed_blocks(self, symbol=None, timeframe=None):
        """
        Получение подтвержденных ордер-блоков из БД
        """
        session = self.data_manager.db_manager.get_session()
        try:
            query = session.query(OrderBlock).filter(OrderBlock.is_confirmed == True)
            
            if symbol:
                query = query.filter(OrderBlock.symbol == symbol)
            if timeframe:
                query = query.filter(OrderBlock.timeframe == timeframe)
            
            blocks = query.order_by(OrderBlock.timestamp.desc()).all()
            return [block.to_dict() for block in blocks]
            
        except Exception as e:
            self.logger.error(f"Ошибка получения ордер-блоков: {e}")
            return []
        finally:
            session.close()
    
    def cleanup_unconfirmed_blocks(self):
        """
        Очистка неподтвержденных ордер-блоков
        """
        session = self.data_manager.db_manager.get_session()
        try:
            deleted_count = session.query(OrderBlock).filter(OrderBlock.is_confirmed == False).delete()
            session.commit()
            self.logger.info(f"Удалено {deleted_count} неподтвержденных ордер-блоков")
            return deleted_count
        except Exception as e:
            session.rollback()
            self.logger.error(f"Ошибка очистки ордер-блоков: {e}")
            return 0
        finally:
            session.close()