import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.simple_main_window import SimpleMainWindow
from database_manager import DatabaseManager

def main():
    """
    Главная функция запуска SMAT приложения
    """
    try:
        print("Запуск SMAT Application...")
        
        # Инициализация базы данных
        db_manager = DatabaseManager()
        print("База данных инициализирована")
        
        # Добавляем тестовые данные если таблица пустая
        db_manager.add_test_order_blocks()
        
        # Создание и запуск главного окна
        root = tk.Tk()
        app = SimpleMainWindow(root, db_manager)
        
        print("Графический интерфейс загружен успешно")
        
        # Запуск главного цикла
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        raise

if __name__ == "__main__":
    main()
