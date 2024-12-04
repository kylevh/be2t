from components.base_component import BaseComponent
import tkinter as tk
from tkinter import colorchooser

class SettingsPage(BaseComponent):
    def create_widgets(self):
        # Get current theme
        theme = self.state_manager.get_state('theme')
        
        # Create color picker button
        self.color_btn = tk.Button(
            self,
            text="Change Primary Color",
            command=self.change_primary_color
        )
        self.color_btn.pack(pady=20)
        
        # Show current color
        self.color_label = tk.Label(
            self,
            text=f"Current Color: {theme['primary_color']}"
        )
        self.color_label.pack()
        
        # Subscribe to theme changes
        self.state_manager.subscribe('theme', self.on_theme_change)
    
    def change_primary_color(self):
        color = colorchooser.askcolor(
            title="Choose Primary Color",
            color=self.state_manager.get_state('theme')['primary_color']
        )
        if color[1]:  # color is ((R,G,B), hex_code)
            self.state_manager.set_state('theme.primary_color', color[1])
    
    def on_theme_change(self, theme):
        self.color_label.config(text=f"Current Color: {theme['primary_color']}")