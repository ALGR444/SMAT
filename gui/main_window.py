# gui/main_window.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QSplitter, QStatusBar)
from PyQt5.QtCore import QTimer, Qt
from gui.orderblock_list import OrderBlockList
from gui.chart_widget import ChartWidget
from gui.styles import get_styles
from data_processor import data_processor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        self.setWindowTitle("SMAT - Smart Money Analysis Tool")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(get_styles()['main_window'])

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal)
        self.chart_widget = ChartWidget()
        self.orderblock_list = OrderBlockList()

        splitter.addWidget(self.chart_widget)
        splitter.addWidget(self.orderblock_list)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе | SMAT v1.0")

    def setup_timers(self):
        # Таймер для обновления статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
        
        # Таймер для первоначальной загрузки данных
        self.init_timer = QTimer()
        self.init_timer.timeout.connect(self.initial_data_load)
        self.init_timer.start(100)  # Короткая задержка для инициализации

    def initial_data_load(self):
        """Первоначальная загрузка данных после создания интерфейса"""
        self.init_timer.stop()
        self.refresh_order_blocks()

    def refresh_order_blocks(self):
        """Обновление списка ордер-блоков"""
        blocks = data_processor.get_order_blocks()
        self.orderblock_list.update_blocks(blocks)

    def update_status(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Получаем количество блоков для статуса
        blocks = data_processor.get_order_blocks()
        confirmed_count = sum(1 for block in blocks if block['confirmed'])
        
        self.status_bar.showMessage(
            f"Готов к работе | {current_time} | "
            f"Блоки: {len(blocks)} (✓{confirmed_count}) | SMAT v1.0"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
