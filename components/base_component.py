from tkinter import Frame
from utils.state_manager import StateManager
from utils.snapshot_processor import SnapshotProcessor
class BaseComponent(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.state_manager = StateManager()
        self.snapshot_processor = SnapshotProcessor()
        self.create_widgets()
    def destroy(self):
        super().destroy()
        
    def create_widgets(self):
        pass
    
    def update_theme(self, theme):
        # Override this in components that need theme updates
        pass