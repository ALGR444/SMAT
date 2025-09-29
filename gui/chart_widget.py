# gui/chart_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from gui.styles import get_styles

class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок графика
        title = QLabel("График ордер-блока")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Заглушка для графика
        chart_placeholder = QLabel("Здесь будет отображаться график\nс уровнями поддержки/сопротивления\nи целями движения цены")
        chart_placeholder.setStyleSheet("""
            QLabel {
                color: #A0AEC0;
                font-size: 14px;
                background-color: #2D3748;
                border: 2px dashed #4A5568;
                border-radius: 10px;
                padding: 50px;
            }
        """)
        chart_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_placeholder)
        
        # Информационная панель
        info_label = QLabel("Таймфрейм: -\nПодтверждение: -\nНаправление: -")
        info_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                background-color: #1A202C;
                border: 1px solid #4A5568;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        self.setStyleSheet(get_styles()['chart_widget'])
