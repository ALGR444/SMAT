# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from database import db
from data_processor import data_processor

def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    # Инициализируем базу данных
    db.init_database()
    
    # Запускаем фоновый обработчик данных
    data_processor.start_processing()
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем главный цикл приложения
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        data_processor.stop_processing()
        sys.exit(0)

if __name__ == "__main__":
    main()
