# gui/styles.py
from config import Config  # ЭТА СТРОКА ДОЛЖНА БЫТЬ!

def get_styles():
    return {
        'main_window': f"""
            QMainWindow {{
                background-color: {Config.COLORS['background']};
                color: {Config.COLORS['text']};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            QMenuBar {{
                background-color: {Config.COLORS['panel']};
                color: {Config.COLORS['text']};
                border: none;
                padding: 5px;
            }}
            QMenuBar::item:selected {{
                background-color: {Config.COLORS['primary']};
                border-radius: 4px;
            }}
            QMenu {{
                background-color: {Config.COLORS['panel']};
                color: {Config.COLORS['text']};
                border: 1px solid {Config.COLORS['border']};
            }}
            QMenu::item:selected {{
                background-color: {Config.COLORS['primary']};
            }}
        """,
        
        'button': f"""
            QPushButton {{
                background-color: {Config.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4299E1;
            }}
            QPushButton:pressed {{
                background-color: #2B6CB0;
            }}
            QPushButton:disabled {{
                background-color: {Config.COLORS['border']};
                color: {Config.COLORS['text_secondary']};
            }}
        """,
        
        'list_widget': f"""
            QListWidget {{
                background-color: {Config.COLORS['panel']};
                border: 1px solid {Config.COLORS['border']};
                border-radius: 5px;
                outline: none;
            }}
            QListWidget::item:selected {{
                background-color: {Config.COLORS['primary']};
                border-radius: 3px;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {Config.COLORS['background']};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Config.COLORS['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #718096;
            }}
        """,
        
        'chart_widget': f"""
            QWidget {{
                background-color: {Config.COLORS['background']};
                border: 1px solid {Config.COLORS['border']};
                border-radius: 5px;
            }}
        """
    }
