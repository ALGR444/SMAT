# order_block_detector.py
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np

class OrderBlockDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_imbalance(self, df: pd.DataFrame, lookback_period: int = 20) -> pd.DataFrame:
        """
        Обнаружение имбалансов на свечном графике
        Имбаланс - это большая свеча с маленькими свечами вокруг
        """
        df = df.copy()
        
        # Вычисляем размер тела свечи и общий размер
        df['body_size'] = abs(df['close'] - df['open'])
        df['total_range'] = df['high'] - df['low']
        df['body_ratio'] = df['body_size'] / df['total_range']
        
        # Вычисляем объем относительно скользящей средней
        df['volume_sma'] = df['volume'].rolling(window=lookback_period).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Ищем имбалансы (большие свечи с высоким объемом)
        df['is_imbalance'] = (
            (df['body_ratio'] > 0.6) &  # Большое тело
            (df['volume_ratio'] > 1.5) &  # Высокий объем
            (df['body_size'] > df['body_size'].rolling(window=lookback_period).mean() * 1.5)  # Большой размер относительно контекста
        )
        
        return df
    
    def find_order_blocks(self, df: pd.DataFrame, timeframe: str) -> List[Dict]:
        """
        Поиск ордер-блоков на основе имбалансов
        """
        if df.empty:
            return []
        
        df_with_imbalance = self.detect_imbalance(df)
        imbalances = df_with_imbalance[df_with_imbalance['is_imbalance']]
        
        order_blocks = []
        
        for idx, row in imbalances.iterrows():
            block = self._analyze_potential_block(df_with_imbalance, idx, timeframe)
            if block:
                order_blocks.append(block)
        
        self.logger.info(f"Найдено {len(order_blocks)} потенциальных ордер-блоков")
        return order_blocks
    
    def _analyze_potential_block(self, df: pd.DataFrame, imbalance_idx: datetime, timeframe: str) -> Optional[Dict]:
        """
        Анализ потенциального ордер-блока вокруг имбаланса
        """
        try:
            current_idx = df.index.get_loc(imbalance_idx)
            if current_idx < 10:  # Нужно достаточно данных для анализа
                return None
            
            # Анализируем свечи до и после имбаланса
            prev_candles = df.iloc[current_idx-5:current_idx]
            next_candles = df.iloc[current_idx+1:current_idx+6]
            
            if len(prev_candles) < 3 or len(next_candles) < 3:
                return None
            
            imbalance_candle = df.loc[imbalance_idx]
            
            # Определяем направление имбаланса
            is_bullish = imbalance_candle['close'] > imbalance_candle['open']
            
            # Проверяем подтверждение (движение цены после имбаланса)
            confirmation = self._check_confirmation(next_candles, is_bullish)
            
            if confirmation['confirmed']:
                block = {
                    'symbol': 'UNKNOWN',  # Будет установлено позже
                    'timeframe': timeframe,
                    'timestamp': imbalance_idx,
                    'imbalance_high': imbalance_candle['high'],
                    'imbalance_low': imbalance_candle['low'],
                    'imbalance_open': imbalance_candle['open'],
                    'imbalance_close': imbalance_candle['close'],
                    'imbalance_volume': imbalance_candle['volume'],
                    'direction': 'BULLISH' if is_bullish else 'BEARISH',
                    'confirmation_strength': confirmation['strength'],
                    'price_target': self._calculate_price_target(imbalance_candle, is_bullish),
                    'created_at': datetime.now()
                }
                return block
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа ордер-блока: {e}")
            return None
    
    def _check_confirmation(self, next_candles: pd.DataFrame, is_bullish: bool) -> Dict:
        """
        Проверка подтверждения ордер-блока
        """
        if next_candles.empty:
            return {'confirmed': False, 'strength': 0}
        
        strength = 0
        
        if is_bullish:
            # Для бычьего блока: цена должна продолжить рост
            price_movement = next_candles['close'].iloc[-1] - next_candles['open'].iloc[0]
            if price_movement > 0:
                strength = min(price_movement / next_candles['open'].iloc[0] * 100, 100)
        else:
            # Для медвежьего блока: цена должна продолжить падение
            price_movement = next_candles['open'].iloc[0] - next_candles['close'].iloc[-1]
            if price_movement > 0:
                strength = min(price_movement / next_candles['open'].iloc[0] * 100, 100)
        
        return {
            'confirmed': strength > 5,  # Минимум 5% движения для подтверждения
            'strength': strength
        }
    
    def _calculate_price_target(self, imbalance_candle: pd.Series, is_bullish: bool) -> float:
        """
        Расчет целевой цены для ордер-блока
        """
        if is_bullish:
            # Для бычьего блока: цель = high + (high - low)
            target = imbalance_candle['high'] + (imbalance_candle['high'] - imbalance_candle['low'])
        else:
            # Для медвежьего блока: цель = low - (high - low)
            target = imbalance_candle['low'] - (imbalance_candle['high'] - imbalance_candle['low'])
        
        return target
