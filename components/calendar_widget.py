from components.base_component import BaseComponent
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime
from typing import List, Set

class CalendarWidget(BaseComponent):
    def __init__(self, parent, *args, **kwargs):
        self.available_dates: Set[str] = set()
        super().__init__(parent, *args, **kwargs)
        self.state_manager.subscribe('snapshots.current_project', self.on_project_change)

    def create_widgets(self):
        self.configure(bg="#2c3e50")  # Match sidebar color
        
        # Calendar header (month/year and navigation)
        self.header_frame = tk.Frame(self, bg="#2c3e50")
        self.header_frame.pack(fill="x", pady=(0, 5))
        
        # Previous month button
        self.prev_button = tk.Button(
            self.header_frame,
            text="<",
            command=self.prev_month,
            relief="flat",
            bg="#2c3e50",
            fg="#ffffff",
            width=2,
            font=("Helvetica", 8)
        )
        self.prev_button.pack(side="left", padx=2)
        
        # Month/Year label
        self.month_label = tk.Label(
            self.header_frame,
            bg="#2c3e50",
            fg="#ffffff",
            font=("Helvetica", 9)
        )
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        self.next_button = tk.Button(
            self.header_frame,
            text=">",
            command=self.next_month,
            relief="flat",
            bg="#2c3e50",
            fg="#ffffff",
            width=2,
            font=("Helvetica", 8)
        )
        self.next_button.pack(side="right", padx=2)
        
        # Calendar grid
        self.calendar_frame = tk.Frame(self, bg="#2c3e50")
        self.calendar_frame.pack(fill="both", expand=True)
        
        # Initialize with current date
        self.current_date = datetime.now()
        self.selected_date = None
        self.update_calendar()
        
    def update_calendar(self):
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        # Add weekday headers
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]  # Shortened weekday names
        for i, day in enumerate(weekdays):
            label = tk.Label(
                self.calendar_frame,
                text=day,
                bg="#2c3e50",
                fg="#6c7293",
                width=3,
                font=("Helvetica", 8)
            )
            label.grid(row=0, column=i, padx=1, pady=1)
            
        # Update month label
        self.month_label.config(
            text=self.current_date.strftime("%b %Y")  # Shortened month name
        )
        
        # Get calendar for current month
        cal = calendar.monthcalendar(
            self.current_date.year,
            self.current_date.month
        )
        
        # Add day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
                    is_available = date_str in self.available_dates
                    
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=3,
                        height=1,
                        relief="flat",
                        state="normal" if is_available else "disabled",
                        bg="#344966" if is_available and date_str != self.selected_date else "#2c3e50",
                        fg="#ffffff" if is_available else "#6c7293",
                        font=("Helvetica", 8),
                        command=lambda d=date_str: self.on_date_select(d)
                    )
                    btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1)
                    
                    # If the date is available and selected, use a different background color
                    if is_available:
                        if date_str == self.selected_date:
                            btn.configure(bg="#4a90e2")  # Highlight color for selected date
                            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#4a90e2"))
                            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#4a90e2"))
                        else:
                            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#3e5a80"))
                            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#344966"))
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
        
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
        
    def on_project_change(self, project_name):
        if project_name:
            dates = self.snapshot_processor.get_project_dates(project_name)
            print(f"Calendar: Available dates: {dates}")  # Debug log
            self.available_dates = set(dates)
            
            self.update_calendar()
            self.pack(fill="x", pady=(20, 20))  # Show calendar
        else:
            self.available_dates = set()
            self.pack_forget()  # Hide calendar
            
    def on_date_select(self, date_str):
        self.selected_date = date_str
        current_project = self.state_manager.get_state('snapshots.current_project')
        if current_project:
            self.snapshot_processor.select_project(current_project, date_str)
        self.update_calendar()  
        # self.state_manager.set_state('snapshots.current_date', date_str)