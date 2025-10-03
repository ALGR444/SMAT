# main.py
import logging
import sys
import os

# Добавляем путь к корневой директории проекта для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector import DataCollector
from block_processor import BlockProcessor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=== SMAT PROJECT: ПОИСК ОРДЕР-БЛОКОВ ===")
    
    # Инициализация сборщика данных
    collector = DataCollector()
    
    # Инициализация символов (если нужно)
    # collector.initialize_symbols()
    
    # Сбор данных для тестовых символов
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
    print(f"\n1. Сбор данных для {len(test_symbols)} символов...")
    collector.collect_multiple_symbols(test_symbols, '15', days_back=30)
    
    # Поиск ордер-блоков
    print("\n2. Поиск ордер-блоков...")
    processor = BlockProcessor()
    blocks = processor.find_blocks_all_symbols(timeframes=['15', '60'])
    
    # Вывод результатов
    print(f"\n=== НАЙДЕННЫЕ ОРДЕР-БЛОКИ ({len(blocks)} всего) ===")
    
    if blocks:
        # Группируем по символам для удобного отображения
        blocks_by_symbol = {}
        for block in blocks:
            symbol = block['symbol']
            if symbol not in blocks_by_symbol:
                blocks_by_symbol[symbol] = []
            blocks_by_symbol[symbol].append(block)
        
        for symbol, symbol_blocks in blocks_by_symbol.items():
            print(f"\n📈 {symbol}: {len(symbol_blocks)} блоков")
            
            for i, block in enumerate(symbol_blocks[:3]):  # Показываем первые 3 блока
                direction_icon = "🟢" if block['direction'] == 'BULLISH' else "🔴"
                print(f"   {direction_icon} Блок {i+1}:")
                print(f"      Таймфрейм: {block['timeframe']}")
                print(f"      Время: {block['timestamp']}")
                print(f"      Направление: {block['direction']}")
                print(f"      Сила подтверждения: {block['confirmation_strength']:.2f}%")
                print(f"      Цель: {block['price_target']:.2f}")
                print(f"      Имбаланс: {block['imbalance_low']:.2f} - {block['imbalance_high']:.2f}")
    else:
        print("❌ Ордер-блоки не найдены")
    
    # Показываем подтвержденные блоки из БД
    print(f"\n3. Подтвержденные блоки из базы данных:")
    confirmed_blocks = processor.get_confirmed_blocks()
    print(f"   В базе данных: {len(confirmed_blocks)} подтвержденных блоков")
    
    # Тестируем очистку неподтвержденных блоков
    print(f"\n4. Очистка неподтвержденных блоков...")
    cleaned_count = processor.cleanup_unconfirmed_blocks()
    print(f"   Удалено блоков: {cleaned_count}")

if __name__ == "__main__":
    main()
