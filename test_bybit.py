#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы с Bybit API
"""

import sys
import os
import pandas as pd

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bybit_api import BybitAPI, download_historical_data
from config import Config

def test_api_connection():
    """Тестирование подключения к API"""
    print("🔗 Тестирование подключения к Bybit API...")
    
    api = BybitAPI()
    
    # Проверка подключения
    if api.test_connection():
        print("✅ Подключение к Bybit API успешно")
        
        # Дополнительная проверка через получение инструментов
        try:
            instruments = api.get_instruments_info("spot")
            if instruments and len(instruments['list']) > 0:
                print("✅ Дополнительная проверка: данные инструментов получены")
                return True
            else:
                print("❌ Не удалось получить данные инструментов")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении инструментов: {e}")
            return False
    else:
        print("❌ Ошибка подключения к Bybit API")
        return False

def test_instruments_info():
    """Тестирование получения информации об инструментах"""
    print("\n📋 Тестирование получения информации об инструментах...")
    
    api = BybitAPI()
    
    try:
        # Спотовые инструменты
        spot_instruments = api.get_instruments_info("spot")
        print(f"✅ Спотовые инструменты: {len(spot_instruments['list'])}")
        
        # Выводим первые 5 инструментов
        print("Примеры инструментов:")
        for instrument in spot_instruments['list'][:5]:
            print(f"  - {instrument['symbol']}: {instrument['baseCoin']}/{instrument['quoteCoin']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка получения информации об инструментах: {e}")
        return False

def test_historical_data():
    """Тестирование загрузки исторических данных"""
    print("\n📊 Тестирование загрузки исторических данных...")
    
    try:
        # Загрузка небольшого количества данных для теста
        df = download_historical_data(
            symbol="BTCUSDT",
            interval="60",  # 1 час
            start_date="2024-01-01",
            end_date="2024-01-03",
            save_to_file=True,
            filename="test_btc_data.csv"
        )
        
        if not df.empty:
            print(f"✅ Успешно загружено {len(df)} записей")
            print(f"✅ Диапазон данных: {df.index[0]} - {df.index[-1]}")
            print(f"✅ Колонки: {list(df.columns)}")
            print(f"✅ Данные сохранены в: data/test_btc_data.csv")
            
            # Базовая статистика
            print("\n📈 Базовая статистика:")
            print(f"  Средняя цена: ${df['close'].mean():.2f}")
            print(f"  Минимальная цена: ${df['close'].min():.2f}")
            print(f"  Максимальная цена: ${df['close'].max():.2f}")
            print(f"  Объем торгов: {df['volume'].sum():.2f} BTC")
            
            return True
        else:
            print("❌ Не удалось загрузить данные")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка загрузки исторических данных: {e}")
        return False

def test_multiple_symbols():
    """Тестирование загрузки данных для нескольких символов"""
    print("\n🔄 Тестирование загрузки данных для нескольких символов...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    results = {}
    
    for symbol in symbols:
        try:
            df = download_historical_data(
                symbol=symbol,
                interval="240",  # 4 часа
                start_date="2024-01-01",
                end_date="2024-01-02",
                save_to_file=False
            )
            
            if not df.empty:
                results[symbol] = len(df)
                print(f"  ✅ {symbol}: {len(df)} записей")
            else:
                results[symbol] = 0
                print(f"  ❌ {symbol}: нет данных")
                
        except Exception as e:
            results[symbol] = f"ошибка: {e}"
            print(f"  ❌ {symbol}: ошибка - {e}")
    
    return results

def test_data_quality():
    """Тестирование качества данных"""
    print("\n🔍 Тестирование качества данных...")
    
    try:
        df = download_historical_data(
            symbol="BTCUSDT",
            interval="60",
            start_date="2024-01-01",
            end_date="2024-01-02",
            save_to_file=False
        )
        
        if not df.empty:
            # Проверяем наличие всех необходимых колонок
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if not missing_columns:
                print("✅ Все необходимые колонки присутствуют")
            else:
                print(f"❌ Отсутствуют колонки: {missing_columns}")
                return False
            
            # Проверяем на наличие NaN значений
            nan_count = df.isnull().sum().sum()
            if nan_count == 0:
                print("✅ NaN значения отсутствуют")
            else:
                print(f"⚠️  Обнаружено {nan_count} NaN значений")
            
            # Проверяем корректность цен (high >= low)
            invalid_prices = df[df['high'] < df['low']]
            if len(invalid_prices) == 0:
                print("✅ Цены корректны (high >= low)")
            else:
                print(f"❌ Обнаружено {len(invalid_prices)} записей с high < low")
                return False
            
            # Проверяем временные метки
            time_diff = df.index.to_series().diff().dropna()
            expected_interval = pd.Timedelta(hours=1)  # для 60-минутного интервала
            irregular_intervals = time_diff[time_diff != expected_interval]
            
            if len(irregular_intervals) == 0:
                print("✅ Временные интервалы корректны")
            else:
                print(f"⚠️  Обнаружено {len(irregular_intervals)} нерегулярных интервалов")
            
            return True
        else:
            print("❌ Нет данных для проверки качества")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки качества данных: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("SMAT Project - Comprehensive Bybit API Test")
    print("=" * 60)
    
    # Проверяем конфигурацию
    print("🔧 Проверка конфигурации...")
    Config.validate()
    
    # Запускаем тесты
    tests = [
        test_api_connection,
        test_instruments_info,
        test_historical_data,
        test_multiple_symbols,
        test_data_quality
    ]
    
    results = {}
    for test in tests:
        try:
            result = test()
            results[test.__name__] = result
        except Exception as e:
            results[test.__name__] = f"Ошибка: {e}"
    
    # Выводим итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed_tests = sum(1 for result in results.values() if result is True)
    total_tests = len(tests)
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result is True else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Результат: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🎯 Этап 1 - интеграция с Bybit API завершен!")
        print("🚀 Модуль готов к использованию в проекте SMAT.")
    else:
        print(f"\n⚠️  Пройдено {passed_tests} из {total_tests} тестов")
        print("❌ Требуется дополнительная отладка")

if __name__ == "__main__":
    main()
