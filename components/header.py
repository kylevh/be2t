from components.base_component import BaseComponent
import tkinter as tk
import json
import os

class Header(BaseComponent):
    def create_widgets(self):
        # Main container with padding
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill="x", padx=40, pady=20)
        
        # Left section - Project info
        self.info_frame = tk.Frame(self.main_container)
        self.info_frame.pack(side="left", fill="y")
        
        self.project_label = tk.Label(
            self.info_frame,
            text="No Project Selected",
            font=("Helvetica", 24, "bold")
        )
        self.project_label.pack(anchor="w")
        
        self.date_label = tk.Label(
            self.info_frame,
            text="",
            font=("Helvetica", 14),
            fg="#666666"
        )
        self.date_label.pack(anchor="w")
        
        # Right section - Stats
        self.stats_frame = tk.Frame(self.main_container)
        self.stats_frame.pack(side="right", fill="y")
        
        # Create stat boxes
        self.create_stat_boxes()
        
        # Subscribe to state changes
        self.state_manager.subscribe('snapshots.current_project', self.update_display)
        self.state_manager.subscribe('snapshots.current_date', self.update_display)
        self.state_manager.subscribe('snapshots.current_snapshot', self.update_display)
        self.state_manager.subscribe('theme', self.update_theme)
        
        # Initial theme
        self.update_theme(self.state_manager.get_state('theme'))
        
    def create_stat_boxes(self):
        # Stats layout - horizontal
        stats = [
            # ("Total Test Cases", "total_test_cases", None),  # None means default color
            ("Passed Cases", "total_passed_cases", "#28a745"),  # Green
            ("Failed Cases", "total_failed_cases", "#dc3545"),  # Red
            ("Passed Steps", "total_passed_steps", "#28a745"),  # Green
            ("Failed Steps", "total_failed_steps", "#dc3545"),  # Red
            ("Coverage", "coverage_percentage", None)
        ]
        
        for label, key, color in stats:
            # Stat box container
            box_frame = tk.Frame(
                self.stats_frame,
                bg="#f8f9fa",
                padx=11,
                pady=8,
                relief="flat",
                borderwidth=1
            )
            box_frame.pack(side="left", padx=4)
            
            # Stat value
            value_label = tk.Label(
                box_frame,
                text="N/A",
                font=("Helvetica", 14, "bold"),
                bg="#f8f9fa",
                fg=color if color else "#000000"  # Use color if provided, else black
            )
            value_label.pack()

            # Store the default color for theme updates
            if color:
                setattr(self, f"{key}_color", color)
            
            # Stat label
            tk.Label(
                box_frame,
                text=label,
                font=("Helvetica", 9),
                fg="#666666",
                bg="#f8f9fa"
            ).pack()
            
            # Store reference to value label
            setattr(self, f"{key}_label", value_label)

    def update_display(self, *args):
        current_project = self.state_manager.get_state('snapshots.current_project')
        current_date = self.state_manager.get_state('snapshots.current_date')
        current_snapshot = self.state_manager.get_state('snapshots.current_snapshot')
        
        if not current_project:
            self.project_label.config(text="Select A Project")
            self.date_label.config(text="")
            self.reset_stats()
            return

        # Format date
        formatted_date = ""
        if current_date:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(current_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')  # e.g., "Monday, December 4, 2024"
            except ValueError:
                formatted_date = current_date
            
        # Update project and date labels
        self.project_label.config(text=current_project)
        self.date_label.config(text=formatted_date)
        
        # Update stats if we have a snapshot
        if current_project and current_date and current_snapshot:
            self.update_stats(current_project, current_date, current_snapshot)
        else:
            self.reset_stats()

    def update_stats(self, project, date, snapshot_file):
        # Construct path to snapshot file
        snapshot_path = os.path.join('soap', 'snapshots', date, project, snapshot_file)
        
        try:
            with open(snapshot_path, 'r') as f:
                data = json.load(f)
                metrics = data.get('metrics', {})
                
                # Update stat labels using the metrics object
                self.total_passed_cases_label.config(text=str(metrics.get('passedCaseCount', 'N/A')))
                self.total_failed_cases_label.config(text=str(metrics.get('failedCaseCount', 'N/A')))
                self.total_passed_steps_label.config(text=str(metrics.get('passedStepCount', 'N/A')))
                self.total_failed_steps_label.config(text=str(metrics.get('failedStepCount', 'N/A')))
                self.coverage_percentage_label.config(text=f"{round(metrics.get('coveragePercentage', 'N/A'))}%")
        except Exception as e:
            print(f"Error loading snapshot data: {e}")
            self.reset_stats()

    def reset_stats(self):
        # Reset all stat labels to 0
        for key in [ 'total_passed_cases', 'total_failed_cases', 'total_passed_steps', 'total_failed_steps', 'coverage_percentage']:
            label = getattr(self, f"{key}_label")
            label.config(text="N/A")

    def update_theme(self, theme):
        self.configure(bg=theme['background_color'])
        self.main_container.configure(bg=theme['background_color'])
        self.info_frame.configure(bg=theme['background_color'])
        self.stats_frame.configure(bg=theme['background_color'])
        self.project_label.configure(
            bg=theme['background_color'],
            fg=theme['primary_color']
        )
        self.date_label.configure(
            bg=theme['background_color'],
            fg=theme['text_color']
        )