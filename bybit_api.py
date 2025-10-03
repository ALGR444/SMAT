# bybit_api.py
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional

class BybitAPI:
    def __init__(self, config=None):
        self.base_url = "https://api.bybit.com"
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def get_kline_data(self, symbol: str, interval: str, 
                      start_time: Optional[int] = None, 
                      end_time: Optional[int] = None, 
                      limit: int = 200) -> List[Dict]:
        """
        Получить исторические данные свечей с преобразованием в унифицированный формат
        """
        try:
            endpoint = "/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            if start_time:
                params['start'] = start_time
            if end_time:
                params['end'] = end_time
            
            response = requests.get(self.base_url + endpoint, params=params)
            data = response.json()
            
            if data['retCode'] != 0:
                self.logger.error(f"Bybit API error: {data['retMsg']}")
                return []
            
            klines = []
            for item in data['result']['list']:
                klines.append({
                    'timestamp': datetime.fromtimestamp(int(item[0]) / 1000),
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                    'volume': float(item[5]),
                    'turnover': float(item[6])
                })
            
            return klines[::-1]  # Возвращаем в хронологическом порядке
            
        except Exception as e:
            self.logger.error(f"Error fetching kline data for {symbol}: {e}")
            return []
    
    def get_multiple_klines(self, symbol: str, interval: str, 
                           start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Получить данные за большой период времени (с автоматической разбивкой на запросы)
        """
        all_klines = []
        current_start = start_time
        
        while current_start < end_time:
            klines = self.get_kline_data(
                symbol=symbol,
                interval=interval,
                start_time=int(current_start.timestamp() * 1000),
                limit=200
            )
            
            if not klines:
                break
                
            all_klines.extend(klines)
            current_start = klines[-1]['timestamp'] + timedelta(minutes=self._interval_to_minutes(interval))
            
            time.sleep(0.1)  # Rate limiting
            
        return all_klines
    
    def get_symbols_info(self) -> List[str]:
        """
        Получить список доступных торговых пар
        """
        try:
            endpoint = "/v5/market/instruments-info"
            params = {'category': 'spot'}
            
            response = requests.get(self.base_url + endpoint, params=params)
            data = response.json()
            
            if data['retCode'] != 0:
                self.logger.error(f"Bybit API error: {data['retMsg']}")
                return []
            
            symbols = [item['symbol'] for item in data['result']['list'] 
                      if item['quoteCoin'] == 'USDT' and item['status'] == 'Trading']
            
            return symbols
            
        except Exception as e:
            self.logger.error(f"Error fetching symbols info: {e}")
            return []
    
    def _interval_to_minutes(self, interval: str) -> int:
        """Конвертировать интервал в минуты"""
        interval_map = {
            '1': 1, '3': 3, '5': 5, '15': 15, '30': 30,
            '60': 60, '120': 120, '240': 240, '360': 360,
            'D': 1440, 'W': 10080, 'M': 43200
        }
        return interval_map.get(interval, 1)
