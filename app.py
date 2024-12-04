import tkinter as tk
from components.header import Header
from components.sidebar import Sidebar
from pages.home_page import HomePage
from utils.state_manager import StateManager

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize state manager
        self.state_manager = StateManager()
        self.state_manager.subscribe('theme', self.apply_theme)

        # Initialize snapshot processor
        # self.snapshot_processor = SnapshotProcessor()
        # self.snapshot_processor.subscribe('snapshots', self.update_snapshots)
        
        # App settings
        self.title("BEATT Internal Tool")
        self.geometry("1200x650")
        
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")
        
        # Header
        self.header = Header(self)
        self.header.pack(fill="x")
        
        # Current page
        self.current_page = HomePage(self)
        self.current_page.pack(expand=True, fill="both")
    
    def switch_page(self, page_class):
        # Remove current page
        if hasattr(self, 'current_page') and self.current_page:
            self.current_page.destroy()
        # Create and show new page
        self.current_page = page_class(self)
        self.current_page.pack(expand=True, fill="both")
    
    def apply_theme(self, theme):
        # Apply theme to root window
        self.configure(bg=theme['background_color'])
        # You might want to update all children
        self.update_widgets_theme(self, theme)

    def update_widgets_theme(self, widget, theme):
        # Recursively update all widgets
        try:
            widget.configure(bg=theme['background_color'])
            widget.configure(fg=theme['text_color'])
        except:
            pass
        
        # for child in widget.winfo_children():
        #     self.update_widgets_theme(child, theme)
    