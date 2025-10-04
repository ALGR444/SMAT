import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_manager import DatabaseManager

class SimpleMainWindow:
    def __init__(self, root, db_manager=None):
        self.root = root
        self.db_manager = db_manager
        self.setup_window()
        self.create_widgets()
        
        # Загружаем данные из БД
        if self.db_manager:
            self.load_order_blocks()
    
    def setup_window(self):
        self.root.title("SMAT - Smart Money Analysis Tool")
        self.root.geometry("1200x700")
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Order blocks list
        left_frame = ttk.LabelFrame(main_frame, text="Найденные ордер-блоки", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel - Chart
        right_frame = ttk.LabelFrame(main_frame, text="График", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Кнопка обновления
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Обновить", command=self.load_order_blocks).pack(side=tk.LEFT)
        
        # Order blocks list
        columns = ("ID", "Symbol", "Timeframe", "Direction", "Confidence", "Price", "Confirmed", "Time")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
        
        # Настройка столбцов
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        self.info_label = ttk.Label(right_frame, text="Выберите ордер-блок для отображения графика")
        self.info_label.pack(pady=20)
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="Загрузка данных...")
        self.status_label.pack(fill=tk.X, pady=(5, 0))
    
    def load_order_blocks(self):
        """Load order blocks from database"""
        try:
            self.status_label.config(text="Загрузка данных...")
            
            blocks = self.db_manager.get_order_blocks()
            print(f"Loaded {len(blocks)} order blocks from database")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add blocks to treeview
            for block in blocks:
                # Структура: id, symbol, timeframe, direction, confirmation_strength, imbalance_high, is_confirmed, timestamp
                block_id, symbol, timeframe, direction, confidence, price_level, is_confirmed, timestamp = block
                
                # Форматирование данных
                direction_icon = "🟢 UP" if direction == 'up' else "🔴 DOWN"
                confidence_pct = f"{confidence*100:.0f}%"
                price_str = f"{price_level:.2f}"
                confirmed_icon = "✅" if is_confirmed else "❌"
                time_str = timestamp.split(' ')[0] if timestamp else "N/A"
                
                self.tree.insert("", "end", values=(
                    block_id, symbol, timeframe, direction_icon, 
                    confidence_pct, price_str, confirmed_icon, time_str
                ))
            
            # Update status
            self.status_label.config(text=f"Загружено блоков: {len(blocks)}")
            self.info_label.config(text=f"Загружено {len(blocks)} ордер-блоков")
                
        except Exception as e:
            print(f"Error loading order blocks: {e}")
            self.status_label.config(text=f"Ошибка: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager()
    app = SimpleMainWindow(root, db_manager)
    root.mainloop()
