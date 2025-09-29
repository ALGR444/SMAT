"""
Модуль для работы с API Bybit
Часть проекта SMAT (Smart Market Analysis Tool)
"""

import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bybit_api')


class BybitAPI:
    """
    Класс для взаимодействия с API Bybit
    """
    
    # Базовые URL для разных типов API
    BASE_URL = "https://api.bybit.com"
    PUBLIC_API_URL = f"{BASE_URL}/v5/market"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Инициализация клиента Bybit API
        
        Args:
            api_key: API ключ (опционально, берется из .env если не указан)
            api_secret: API секрет (опционально, берется из .env если не указан)
        """
        # Берем ключи из аргументов или из переменных окружения
        self.api_key = api_key or os.getenv('BYBIT_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BYBIT_API_SECRET', '')
        
        self.session = requests.Session()
        
        # Установка общих заголовков
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SMAT/1.0'
        }
        
        # Добавляем API ключ в заголовки если он есть
        if self.api_key:
            headers['X-BAPI-API-KEY'] = self.api_key
            
        self.session.headers.update(headers)
        
        logger.info("BybitAPI инициализирован")
    
    def get_kline_data(
        self,
        symbol: str,
        interval: str,
        from_timestamp: Optional[int] = None,
        limit: int = 200,
        category: str = "spot"
    ) -> pd.DataFrame:
        """
        Получение исторических данных (K-line)
        
        Args:
            symbol: Торговая пара (например: "BTCUSDT")
            interval: Таймфрейм (1,3,5,15,30,60,120,240,360,720,D,M,W)
            from_timestamp: Начальная timestamp в миллисекундах
            limit: Количество записей (макс. 200)
            category: Категория (spot, linear, inverse)
            
        Returns:
            pd.DataFrame с историческими данными
        """
        endpoint = f"{self.PUBLIC_API_URL}/kline"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'category': category
        }
        
        if from_timestamp:
            params['start'] = from_timestamp
        
        try:
            logger.info(f"Запрос данных для {symbol}, интервал {interval}")
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['retCode'] != 0:
                error_msg = f"Bybit API error: {data['retMsg']} (code: {data['retCode']})"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            if not data['result'] or not data['result']['list']:
                logger.warning(f"Нет данных для {symbol}")
                return pd.DataFrame()
            
            # Преобразуем данные в DataFrame
            df = self._parse_kline_data(data['result']['list'])
            
            logger.info(f"Успешно получено {len(df)} записей для {symbol}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка обработки данных: {e}")
            raise
    
    def _parse_kline_data(self, kline_list: List[List]) -> pd.DataFrame:
        """
        Парсинг сырых данных K-line в DataFrame
        
        Args:
            kline_list: Список данных свечей
            
        Returns:
            pd.DataFrame с структурированными данными
        """
        columns = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'turnover'
        ]
        
        df = pd.DataFrame(kline_list, columns=columns)
        
        # Конвертируем типы данных
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col])
        
        # Конвертируем timestamp в datetime
        df['timestamp'] = pd.to_numeric(df['timestamp'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Устанавливаем datetime как индекс
        df.set_index('datetime', inplace=True)
        
        # Сортируем по времени (от старых к новым)
        df.sort_index(inplace=True)
        
        return df
    
    def get_multiple_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime] = None,
        category: str = "spot"
    ) -> pd.DataFrame:
        """
        Получение больших объемов данных через множественные запросы
        
        Args:
            symbol: Торговая пара
            interval: Таймфрейм
            start_time: Время начала (строка или datetime)
            end_time: Время окончания (строка или datetime, по умолчанию сейчас)
            category: Категория
            
        Returns:
            pd.DataFrame с объединенными данными
        """
        # Конвертируем время в timestamp
        if isinstance(start_time, str):
            start_time = pd.to_datetime(start_time)
        if end_time is None:
            end_time = datetime.now()
        elif isinstance(end_time, str):
            end_time = pd.to_datetime(end_time)
        
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        all_data = []
        current_start = start_timestamp
        
        # Максимальное количество итераций для избежания бесконечного цикла
        max_iterations = 1000
        iteration = 0
        
        logger.info(f"Начало загрузки данных {symbol} с {start_time} по {end_time}")
        
        while current_start < end_timestamp and iteration < max_iterations:
            try:
                df_batch = self.get_kline_data(
                    symbol=symbol,
                    interval=interval,
                    from_timestamp=current_start,
                    limit=200,
                    category=category
                )
                
                if df_batch.empty:
                    logger.info("Получен пустой батч, завершаем загрузку")
                    break
                
                # Получаем timestamp последней свечи
                last_timestamp = df_batch['timestamp'].iloc[-1]
                
                # Проверяем, не застряли ли мы на одном месте
                if all_data and last_timestamp <= current_start:
                    logger.warning("Не прогрессируем во времени, завершаем загрузку")
                    break
                
                # Добавляем данные
                all_data.append(df_batch)
                
                # Сдвигаем начало для следующего запроса
                current_start = last_timestamp + 1
                
                # Пауза для избежания лимитов API
                time.sleep(0.2)
                
                iteration += 1
                
                if iteration % 10 == 0:
                    logger.info(f"Загружено {len(all_data)} батчей...")
                
            except Exception as e:
                logger.error(f"Ошибка при получении батча {iteration}: {e}")
                break
        
        if not all_data:
            logger.warning("Не удалось загрузить никаких данных")
            return pd.DataFrame()
        
        # Объединяем все данные
        result_df = pd.concat(all_data, ignore_index=False)
        
        # Удаляем дубликаты и сортируем
        result_df = result_df[~result_df.index.duplicated(keep='first')]
        result_df.sort_index(inplace=True)
        
        # Обрезаем по end_time
        result_df = result_df[result_df.index <= pd.to_datetime(end_timestamp, unit='ms')]
        
        logger.info(f"Всего получено {len(result_df)} записей за период с {start_time} по {end_time}")
        return result_df
    
    def get_instruments_info(self, category: str = "spot") -> Dict:
        """
        Получение информации о доступных инструментах
        
        Args:
            category: Категория (spot, linear, inverse)
            
        Returns:
            Словарь с информацией об инструментах
        """
        endpoint = f"{self.PUBLIC_API_URL}/instruments-info"
        
        params = {
            'category': category
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['retCode'] != 0:
                error_msg = f"Bybit API error: {data['retMsg']} (code: {data['retCode']})"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return data['result']
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об инструментах: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения к API через рабочий эндпоинт
        """
        try:
            # Используем рабочий эндпоинт вместо server-time
            endpoint = f"{self.PUBLIC_API_URL}/instruments-info"
            params = {'category': 'spot', 'limit': 1}
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data['retCode'] == 0
            
        except Exception as e:
            logger.error(f"Ошибка подключения к Bybit API: {e}")
            return False
    
    def get_server_time(self) -> Dict:
        """
        Получение серверного времени Bybit через альтернативный метод
        """
        try:
            # Получаем время из данных свечи
            endpoint = f"{self.PUBLIC_API_URL}/kline"
            params = {
                'symbol': 'BTCUSDT',
                'interval': '1',
                'limit': 1,
                'category': 'spot'
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['retCode'] != 0:
                raise Exception(f"API error: {data['retMsg']}")
            
            if data['result']['list']:
                timestamp = int(data['result']['list'][0][0])
                return {
                    'timeSecond': timestamp // 1000,
                    'timeNano': timestamp * 1000000
                }
            else:
                raise Exception("No data received for server time")
                
        except Exception as e:
            logger.error(f"Ошибка получения серверного времени: {e}")
            raise


# Функции для удобного использования
def download_historical_data(
    symbol: str,
    interval: str,
    start_date: str,
    end_date: str = None,
    save_to_file: bool = False,
    filename: str = None,
    category: str = "spot"
) -> pd.DataFrame:
    """
    Упрощенная функция для загрузки исторических данных
    
    Args:
        symbol: Торговая пара
        interval: Таймфрейм
        start_date: Дата начала (формат: 'YYYY-MM-DD')
        end_date: Дата окончания (формат: 'YYYY-MM-DD')
        save_to_file: Сохранять ли в файл
        filename: Имя файла для сохранения
        category: Категория торговли
        
    Returns:
        pd.DataFrame с историческими данными
    """
    api = BybitAPI()
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    df = api.get_multiple_klines(
        symbol=symbol,
        interval=interval,
        start_time=start_date,
        end_time=end_date,
        category=category
    )
    
    if save_to_file and not df.empty:
        if filename is None:
            filename = f"{symbol}_{interval}_{start_date}_to_{end_date}.csv"
        
        # Создаем директорию если не существует
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        df.to_csv(filepath)
        logger.info(f"Данные сохранены в файл: {filepath}")
    
    return df


# Пример использования
if __name__ == "__main__":
    # Тестирование модуля
    api = BybitAPI()
    
    print("=" * 50)
    print("SMAT Project - Testing Bybit API Module")
    print("=" * 50)
    
    # Проверка подключения
    if api.test_connection():
        print("✅ Подключение к Bybit API успешно")
        
        # Получаем серверное время
        try:
            server_time = api.get_server_time()
            print(f"✅ Серверное время Bybit: {server_time['timeSecond']}")
        except Exception as e:
            print(f"⚠️  Не удалось получить серверное время: {e}")
    else:
        print("❌ Ошибка подключения к Bybit API")
        exit(1)
    
    # Пример загрузки данных
    try:
        # Получение информации о доступных инструментах
        instruments = api.get_instruments_info("spot")
        print(f"✅ Доступно спотовых инструментов: {len(instruments['list'])}")
        
        # Загрузка исторических данных
        print("\n📊 Загрузка тестовых данных...")
        df = download_historical_data(
            symbol="BTCUSDT",
            interval="60",  # 1 час
            start_date="2024-01-01",
            end_date="2024-01-02",
            save_to_file=True
        )
        
        if not df.empty:
            print(f"✅ Загружено данных: {len(df)} записей")
            print("\nПервые 5 записей:")
            print(df.head())
            print(f"\nДиапазон данных: {df.index[0]} - {df.index[-1]}")
            print(f"\nКолонки: {list(df.columns)}")
        else:
            print("❌ Не удалось загрузить данные")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
