# models.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

Base = declarative_base()

class Symbol(Base):
    __tablename__ = 'symbols'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    base_currency = Column(String(10))
    quote_currency = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class KlineData(Base):
    __tablename__ = 'klines'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(5), nullable=False)  # 1, 5, 15, 60, 240, D, W, M
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    turnover = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Составной индекс для быстрого поиска
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class OrderBlock(Base):
    __tablename__ = 'order_blocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(5), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    imbalance_high = Column(Float)
    imbalance_low = Column(Float)
    imbalance_open = Column(Float)
    imbalance_close = Column(Float)
    imbalance_volume = Column(Float)
    direction = Column(String(10))  # BULLISH/BEARISH
    confirmation_strength = Column(Float)
    price_target = Column(Float)
    is_confirmed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp,
            'imbalance_high': self.imbalance_high,
            'imbalance_low': self.imbalance_low,
            'imbalance_open': self.imbalance_open,
            'imbalance_close': self.imbalance_close,
            'imbalance_volume': self.imbalance_volume,
            'direction': self.direction,
            'confirmation_strength': self.confirmation_strength,
            'price_target': self.price_target,
            'is_confirmed': self.is_confirmed
        }

class DatabaseManager:
    def __init__(self, db_path="data/smat.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info(f"База данных инициализирована: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации БД: {e}")
            raise
    
    def get_session(self):
        """Получить сессию базы данных"""
        return self.Session()
    
    def add_symbols(self, symbols_list):
        """Добавить символы в базу данных"""
        session = self.get_session()
        try:
            for symbol_data in symbols_list:
                symbol = session.query(Symbol).filter_by(symbol=symbol_data['symbol']).first()
                if not symbol:
                    new_symbol = Symbol(
                        symbol=symbol_data['symbol'],
                        base_currency=symbol_data.get('base_currency'),
                        quote_currency=symbol_data.get('quote_currency')
                    )
                    session.add(new_symbol)
            
            session.commit()
            self.logger.info(f"Добавлено/обновлено {len(symbols_list)} символов")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Ошибка добавления символов: {e}")
            raise
        finally:
            session.close()