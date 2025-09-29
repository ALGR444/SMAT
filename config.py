# config.py
class Config:
    # Списки для тестирования
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT']
    TIMEFRAMES = ['15', '60', '240']  # минуты
    
    # Настройки обработчика
    REFRESH_INTERVAL = 10  # секунды между циклами обработки
    
    # Bybit API (пока не используется, но добавим для будущего)
    BYBIT_API_KEY = 'your_api_key_here'
    BYBIT_API_SECRET = 'your_api_secret_here'
    
    # Настройки алгоритма поиска ордер-блоков (тестовые)
    MIN_BLOCK_SIZE_PERCENT = 0.5  # минимальный размер блока в %
    CONFIRMATION_CANDLES = 3      # количество свечей для подтверждения

    # Цвета для интерфейса (ДОБАВЛЯЕМ ЭТОТ БЛОК)
    COLORS = {
        'background': '#1A202C',
        'panel': '#2D3748',
        'border': '#4A5568',
        'text': 'white',
        'text_secondary': '#A0AEC0',
        'success': '#00C853',
        'danger': '#FF1744',
        'primary': '#3182CE'
    }
