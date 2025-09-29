"""
Демонстрация работы Bybit API модуля
"""

from bybit_api import download_historical_data, BybitAPI
import pandas as pd

def main():
    print("🚀 ДЕМО-ЗАПУСК SMAT BYBIT API")
    print("=" * 50)
    
    # Создаем экземпляр API
    api = BybitAPI()
    
    # Проверяем подключение
    if api.test_connection():
        print("✅ Подключение к Bybit API успешно")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Демонстрация 1: Базовая загрузка данных
    print("\n1. 📥 БАЗОВАЯ ЗАГРУЗКА ДАННЫХ")
    print("-" * 30)
    
    df_btc = download_historical_data(
        symbol="BTCUSDT",
        interval="60",  # 1 час
        start_date="2024-01-01",
        end_date="2024-01-03",
        save_to_file=True,
        filename="demo_btc_1h.csv"
    )
    
    print(f"Загружено {len(df_btc)} записей BTC/USDT")
    print(f"Период: {df_btc.index[0]} - {df_btc.index[-1]}")
    print(f"Колонки: {list(df_btc.columns)}")
    
    # Демонстрация 2: Разные таймфреймы
    print("\n2. ⏰ РАЗНЫЕ ТАЙМФРЕЙМЫ")
    print("-" * 30)
    
    timeframes = [
        ("15", "15 минут"),
        ("60", "1 час"),
        ("240", "4 часа"), 
        ("D", "1 день")
    ]
    
    for interval, description in timeframes:
        df = download_historical_data(
            symbol="ETHUSDT",
            interval=interval,
            start_date="2024-01-01",
            end_date="2024-01-02",
            save_to_file=False
        )
        print(f"{description}: {len(df)} записей")
    
    # Демонстрация 3: Множественные символы
    print("\n3. 🔄 НЕСКОЛЬКО ТОРГОВЫХ ПАР")
    print("-" * 30)
    
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]
    
    for symbol in symbols:
        df = download_historical_data(
            symbol=symbol,
            interval="240",  # 4 часа
            start_date="2024-01-01",
            end_date="2024-01-02",
            save_to_file=False
        )
        if not df.empty:
            price_change = (df['close'].iloc[-1] / df['open'].iloc[0] - 1) * 100
            print(f"{symbol}: {len(df)} записей, изменение: {price_change:+.2f}%")
    
    # Демонстрация 4: Анализ данных
    print("\n4. 📊 АНАЛИЗ ДАННЫХ")
    print("-" * 30)
    
    if not df_btc.empty:
        print("Анализ BTC/USDT:")
        print(f"• Начальная цена: ${df_btc['open'].iloc[0]:.2f}")
        print(f"• Конечная цена: ${df_btc['close'].iloc[-1]:.2f}")
        print(f"• Изменение: {((df_btc['close'].iloc[-1] / df_btc['open'].iloc[0] - 1) * 100):.2f}%")
        print(f"• Максимальная цена: ${df_btc['high'].max():.2f}")
        print(f"• Минимальная цена: ${df_btc['low'].min():.2f}")
        print(f"• Средний объем: {df_btc['volume'].mean():.2f} BTC/час")
        print(f"• Общий объем: {df_btc['volume'].sum():.2f} BTC")
    
    # Демонстрация 5: Информация о инструментах
    print("\n5. 📋 ИНФОРМАЦИЯ О ИНСТРУМЕНТАХ")
    print("-" * 30)
    
    try:
        instruments = api.get_instruments_info("spot")
        usdt_pairs = [inst for inst in instruments['list'] if inst['quoteCoin'] == 'USDT']
        print(f"Всего USDT пар: {len(usdt_pairs)}")
        
        print("Популярные пары:")
        for pair in usdt_pairs[:5]:
            print(f"  • {pair['symbol']} ({pair['baseCoin']})")
            
    except Exception as e:
        print(f"Ошибка получения информации: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("📁 Данные сохранены в папке 'data/'")
    print("🚀 Модуль готов к использованию!")

if __name__ == "__main__":
    main()