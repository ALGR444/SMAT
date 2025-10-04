import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .orderblock_list import OrderBlockList
from .chart_widget import ChartWidget
# from .styles import configure_styles  # Временно отключим

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_manager import DatabaseManager

class MainWindow:
    def __init__(self, root, db_manager=None):
        self.root = root
        self.db_manager = db_manager
        self.setup_window()
        self.create_widgets()
        # configure_styles()  # Временно отключим
        
        # Загружаем данные из БД после инициализации интерфейса
        if self.db_manager:
            self.load_order_blocks_from_db()
    
    def setup_window(self):
        self.root.title("SMAT - Smart Money Analysis Tool")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
    
    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Order blocks list
        left_panel = ttk.LabelFrame(main_container, text="Найденные ордер-блоки", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel - Chart
        right_panel = ttk.LabelFrame(main_container, text="График", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create order blocks list - исправленная строка
        self.orderblock_list = OrderBlockList()
        self.orderblock_list.create_widgets(left_panel)  # Передаем родителя в отдельный метод
        
        # Create chart widget - исправленная строка
        self.chart_widget = ChartWidget()
        self.chart_widget.create_widgets(right_panel)  # Передаем родителя в отдельный метод
        
        # Connect widgets
        self.orderblock_list.on_block_selected = self.on_block_selected
    
    def on_block_selected(self, block_data):
        """Handle order block selection from the list"""
        self.chart_widget.display_block(block_data)
    
    def load_order_blocks_from_db(self):
        """Load order blocks from database into the interface"""
        try:
            if not self.db_manager:
                print("Database manager not available")
                return
                
            # Get order blocks from database
            blocks = self.db_manager.get_order_blocks()
            print(f"Loaded {len(blocks)} order blocks from database")
            
            # Convert to format expected by OrderBlockList
            formatted_blocks = []
            for block in blocks:
                block_id, symbol, timeframe, block_type, confidence, price_level, timestamp = block
                
                formatted_block = {
                    'id': block_id,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'type': block_type,
                    'confidence': bool(confidence),
                    'price_level': price_level,
                    'timestamp': timestamp
                }
                formatted_blocks.append(formatted_block)
            
            # Load blocks into the order block list
            self.orderblock_list.load_blocks(formatted_blocks)
            
        except Exception as e:
            print(f"Error loading order blocks from database: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager()
    app = MainWindow(root, db_manager)
    root.mainloop()
