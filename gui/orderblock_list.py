# gui/orderblock_list.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QLabel, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
from gui.styles import get_styles
from data_processor import data_processor

class OrderBlockItemWidget(QWidget):
    show_clicked = pyqtSignal(str)
    toggle_confirmed = pyqtSignal(int, bool)

    def __init__(self, block_id, symbol, timeframe, confirmed, direction, parent=None):
        super().__init__(parent)
        self.block_id = block_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.confirmed = confirmed
        self.direction = direction
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        symbol_label = QLabel(self.symbol)
        symbol_label.setStyleSheet("color: white; font-weight: bold;")
        symbol_label.setFixedWidth(70)
        symbol_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(symbol_label)

        timeframe_label = QLabel(self.timeframe)
        timeframe_label.setStyleSheet("color: #A0AEC0;")
        timeframe_label.setFixedWidth(40)
        timeframe_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(timeframe_label)

        confirm_widget = QWidget()
        confirm_layout = QHBoxLayout()
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setAlignment(Qt.AlignCenter)

        self.confirm_check = QCheckBox()
        self.confirm_check.setChecked(self.confirmed)
        self.confirm_check.stateChanged.connect(self.on_confirm_toggle)
        self.confirm_check.setStyleSheet("""
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #718096;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #00C853;
            border: 2px solid #00C853;
        }
        QCheckBox::indicator:unchecked {
            background-color: transparent;
        }
        """)

        confirm_layout.addWidget(self.confirm_check)
        confirm_widget.setLayout(confirm_layout)
        confirm_widget.setFixedWidth(40)
        layout.addWidget(confirm_widget)

        direction_widget = QWidget()
        direction_layout = QHBoxLayout()
        direction_layout.setContentsMargins(0, 0, 0, 0)
        direction_layout.setAlignment(Qt.AlignCenter)

        arrow_label = QLabel()
        arrow_label.setFixedSize(20, 20)
        if self.direction == 'bullish':
            arrow_label.setStyleSheet("""
            QLabel {
                background-color: #00C853;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
            """)
            arrow_label.setText("↑")
        else:
            arrow_label.setStyleSheet("""
            QLabel {
                background-color: #FF1744;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
            """)
            arrow_label.setText("↓")

        direction_layout.addWidget(arrow_label)
        direction_widget.setLayout(direction_layout)
        direction_widget.setFixedWidth(40)
        layout.addWidget(direction_widget)

        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)

        self.show_btn = QPushButton("Показать")
        self.show_btn.setStyleSheet(get_styles()['button'])
        self.show_btn.setFixedSize(70, 25)
        self.show_btn.clicked.connect(self.on_show_clicked)
        button_layout.addWidget(self.show_btn)

        button_widget.setLayout(button_layout)
        button_widget.setFixedWidth(80)
        layout.addWidget(button_widget)

        self.setLayout(layout)
        self.setFixedHeight(40)
        self.setStyleSheet("""
        QWidget {
            background-color: #1A202C;
            border-radius: 5px;
            border: 1px solid #4A5568;
        }
        """)

    def on_show_clicked(self):
        self.show_clicked.emit(f"{self.symbol}_{self.timeframe}")

    def on_confirm_toggle(self, state):
        confirmed = state == Qt.Checked
        self.toggle_confirmed.emit(self.block_id, confirmed)

class OrderBlockList(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        title = QLabel("Найденные ордер-блоки")
        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 16px;
            font-weight: bold;
            background-color: #2D3748;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #4A5568;
        }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        headers_widget = QWidget()
        headers_layout = QHBoxLayout()
        headers_layout.setContentsMargins(10, 5, 10, 5)
        headers_layout.setSpacing(5)

        header1 = QLabel("Пара")
        header1.setStyleSheet("color: #718096; font-weight: bold;")
        header1.setFixedWidth(70)
        header1.setAlignment(Qt.AlignCenter)
        headers_layout.addWidget(header1)

        header2 = QLabel("ТФ")
        header2.setStyleSheet("color: #718096; font-weight: bold;")
        header2.setFixedWidth(40)
        header2.setAlignment(Qt.AlignCenter)
        headers_layout.addWidget(header2)

        header3 = QLabel("Подтв.")
        header3.setStyleSheet("color: #718096; font-weight: bold;")
        header3.setFixedWidth(40)
        header3.setAlignment(Qt.AlignCenter)
        headers_layout.addWidget(header3)

        header4 = QLabel("Напр.")
        header4.setStyleSheet("color: #718096; font-weight: bold;")
        header4.setFixedWidth(40)
        header4.setAlignment(Qt.AlignCenter)
        headers_layout.addWidget(header4)

        header5 = QLabel("Действие")
        header5.setStyleSheet("color: #718096; font-weight: bold;")
        header5.setFixedWidth(80)
        header5.setAlignment(Qt.AlignCenter)
        headers_layout.addWidget(header5)

        headers_widget.setLayout(headers_layout)
        headers_widget.setStyleSheet("background-color: #2D3748; border-radius: 3px;")
        layout.addWidget(headers_widget)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(get_styles()['list_widget'])
        self.list_widget.setSpacing(5)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Очистить список")
        self.clear_btn.setStyleSheet(get_styles()['button'])
        self.clear_btn.clicked.connect(self.clear_list)
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.setStyleSheet(get_styles()['button'])
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setup_timer(self):
        """Таймер для автоматического обновления списка"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_list)
        self.update_timer.start(5000)  # Обновление каждые 5 секунд

    def update_blocks(self, blocks):
        """Обновление списка ордер-блоками из базы данных"""
        self.clear_list()
        for block in blocks:
            self.add_order_block(block)

    def add_order_block(self, block):
        item_widget = OrderBlockItemWidget(
            block_id=block['id'],
            symbol=block['symbol'],
            timeframe=block['timeframe'],
            confirmed=block['confirmed'],
            direction=block['block_type']
        )
        
        item_widget.show_clicked.connect(self.on_show_block)
        item_widget.toggle_confirmed.connect(self.on_toggle_confirmation)
        
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

    def on_show_block(self, block_id):
        print(f"Показываем ордер-блок: {block_id}")

    def on_toggle_confirmation(self, block_id, confirmed):
        """Обработка изменения статуса подтверждения"""
        success = data_processor.update_order_block_confirmation(block_id, confirmed)
        if success:
            print(f"Статус ордер-блока {block_id} изменен на: {'Подтвержден' if confirmed else 'Не подтвержден'}")

    def clear_list(self):
        self.list_widget.clear()

    def refresh_list(self):
        """Обновление списка из базы данных"""
        blocks = data_processor.get_order_blocks()
        self.update_blocks(blocks)
