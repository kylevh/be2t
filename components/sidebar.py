from components.base_component import BaseComponent
import tkinter as tk
from tkinter import ttk
from utils.snapshot_processor import SnapshotProcessor
from components.calendar_widget import CalendarWidget

class Sidebar(BaseComponent):
    def create_widgets(self):
        self.snapshot_processor = SnapshotProcessor()
        # Configure sidebar style
        self.configure(width=200, bg="#2c3e50")
        
        # Create main container
        self.main_container = tk.Frame(self, bg="#2c3e50")
        self.main_container.pack(fill="y", expand=True, padx=15)

        # Project selection dropdown
        self.create_project_dropdown()

        # Navigation buttons
        self.create_nav_buttons()
        
        # Calendar widget (initially hidden)
        self.calendar = CalendarWidget(self.main_container)
    
    def create_project_dropdown(self):
        # Project selection label
        self.project_label = tk.Label(
            self.main_container,
            text="SELECT PROJECT",
            font=("Helvetica", 9),
            bg="#2c3e50",
            fg="#6c7293"  # Subtle gray color for labels
        )
        self.project_label.pack(pady=(20, 5), anchor="w")

        # Style the combobox
        style = ttk.Style()
        style.configure("Custom.TCombobox", 
            background="#2d2d44",
            fieldbackground="#2d2d44",
            foreground="#ffffff",
            arrowcolor="#ffffff"
        )
        
        # Project dropdown
        self.project_var = tk.StringVar()
        self.project_dropdown = ttk.Combobox(
            self.main_container,
            textvariable=self.project_var,
            state="readonly",
            width=25,
            style="Custom.TCombobox"
        )

        print("ALL PROJECTS:", self.snapshot_processor.get_all_projects())
        self.project_dropdown['values'] = self.snapshot_processor.get_all_projects()
        self.project_dropdown.pack(pady=(0, 25))
        self.project_dropdown.bind('<<ComboboxSelected>>', self.on_project_select)
    
    def create_nav_buttons(self):
        # Navigation buttons container
        self.nav_container = tk.Frame(self.main_container, bg="#2c3e50")
        self.nav_container.pack(fill="x", padx=10, pady=10)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Add navigation buttons
        self.add_nav_button("Home", self.navigate_home)
        self.add_nav_button("Snapshot", self.navigate_snapshot)
        self.add_nav_button("Analysis", self.navigate_analysis)
        self.add_nav_button("Settings", self.navigate_settings)
        
    def add_nav_button(self, text, command):
        btn = tk.Button(
            self.nav_container,
            text=text,
            command=command,
            font=("Helvetica", 10),
            width=22,
            relief="flat",
            cursor="hand2",
            bg="#34495e",  # Slightly lighter than sidebar for contrast
            fg="#ffffff",
            activebackground="#3498db",  # Blue highlight on click
            activeforeground="#ffffff",
            bd=1,  # Add a subtle border
            pady=12  # Add vertical padding
        )
        btn.pack(pady=3, fill="x")
        
        # Enhanced hover effect
        btn.bind("<Enter>", lambda e, btn=btn: btn.configure(bg="#3498db"))
        btn.bind("<Leave>", lambda e, btn=btn: btn.configure(bg="#34495e"))
        
        self.nav_buttons.append(btn)
    
    def navigate_home(self):
        from pages.home_page import HomePage
        self.master.switch_page(HomePage)

    def navigate_settings(self):
        from pages.settings_page import SettingsPage
        self.master.switch_page(SettingsPage)
    
    def navigate_analysis(self):
        from pages.analysis_page import AnalysisPage
        self.master.switch_page(AnalysisPage)
    
    def navigate_snapshot(self):
        from pages.snapshot_page import SnapshotPage
        self.master.switch_page(SnapshotPage)
    
    def on_project_select(self, event):
        selected_project = self.project_var.get()
        self.snapshot_processor.select_project(selected_project)
        # print(self.state_manager.get_state('snapshots'))

    def on_date_select(self, date):
        # Handle date selection - you can add more functionality here (HANDLED IN CALENDAR WIDGET)
        print(f"Selected date: {date}")
    