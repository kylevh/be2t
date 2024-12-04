from components.base_component import BaseComponent
import tkinter as tk
from tkinter import ttk
import json
import os

class HomePage(BaseComponent):
    def destroy(self):
        self.state_manager.unsubscribe('snapshots.current_project', self.update_display)
        self.state_manager.unsubscribe('snapshots.current_date', self.update_display)
        self.state_manager.unsubscribe('snapshots.current_snapshot', self.update_display)
        super().destroy()

    def create_widgets(self):
        # Subscribe to state changes (same as before)
        self.state_manager.subscribe('snapshots.current_project', self.update_display)
        self.state_manager.subscribe('snapshots.current_date', self.update_display)
        self.state_manager.subscribe('snapshots.current_snapshot', self.update_display)
        
        # Main container with dark background
        self.main_container = tk.Frame(self, bg="#f0f2f5")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Project header with new styling
        self.header_frame = tk.Frame(self.main_container, bg="#ffffff", pady=20, padx=30)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.project_label = tk.Label(
            self.header_frame,
            text="No Project Selected",
            font=("Helvetica", 28, "bold"),
            bg="#ffffff"
        )
        self.project_label.pack(anchor="w")
        
        self.date_label = tk.Label(
            self.header_frame,
            text="",
            font=("Helvetica", 14),
            fg="#666666",
            bg="#ffffff"
        )
        self.date_label.pack(anchor="w")
        
        # Status indicator
        self.status_frame = tk.Frame(self.header_frame, bg="#ffffff")
        self.status_frame.pack(anchor="w", pady=(10, 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Status: ",
            font=("Helvetica", 12),
            bg="#ffffff"
        )
        self.status_label.pack(side="left")
        
        self.status_value = tk.Label(
            self.status_frame,
            text="N/A",
            font=("Helvetica", 12, "bold"),
            bg="#ffffff"
        )
        self.status_value.pack(side="left")
        
        # Create metrics grid
        self.create_metrics_grid()
        
        # Initial update
        self.update_display()

    
    def create_metrics_grid(self):
        # Metrics container with white background
        self.metrics_frame = tk.Frame(self.main_container, bg="#ffffff", padx=30, pady=30)
        self.metrics_frame.pack(fill="both", expand=True)
        
        # Define metrics to display
        metrics = [
            ("Test Suites", "suite_count"),
            ("Test Cases", "case_count"),
            ("Passed Cases", "passed_case_count"),
            ("Failed Cases", "failed_case_count"),
            ("Total Steps", "step_count"),
            ("Passed Steps", "passed_step_count"),
            ("Failed Steps", "failed_step_count"),
            ("Coverage", "coverage_percentage", True)  # True indicates percentage
        ]
        
        # Create 4x2 grid of metrics
        for i, (label, key, *args) in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            metric_frame = tk.Frame(
                self.metrics_frame,
                bg="#ffffff",
                relief="flat"
            )
            metric_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Configure grid weights
            self.metrics_frame.grid_columnconfigure(col, weight=1)
            
            # Metric value
            value_label = tk.Label(
                metric_frame,
                text="0",
                font=("Helvetica", 24, "bold"),
                bg="#ffffff",
                fg="#2d3436"
            )
            value_label.pack()
            
            # Metric label
            tk.Label(
                metric_frame,
                text=label,
                font=("Helvetica", 12),
                fg="#636e72",
                bg="#ffffff"
            ).pack()
            
            # Store reference
            setattr(self, f"{key}_label", value_label)

    
    def update_stats(self, project, date, snapshot_file):
        snapshot_path = os.path.join('soap', 'snapshots', date, project, snapshot_file)
        
        try:
            with open(snapshot_path, 'r') as f:
                data = json.load(f)
                metrics = data.get('metrics', {})
                
                # Update status with color
                status = metrics.get('projectStatus', 'N/A')
                self.status_value.config(
                    text=status.upper(),
                    fg="#27ae60" if status.lower() == "passed" else "#e74c3c"
                )
                
                # Update metric labels
                self.suite_count_label.config(text=str(metrics.get('suiteCount', 0)))
                self.case_count_label.config(text=str(metrics.get('caseCount', 0)))
                self.passed_case_count_label.config(text=str(metrics.get('passedCaseCount', 0)))
                self.failed_case_count_label.config(text=str(metrics.get('failedCaseCount', 0)))
                self.step_count_label.config(text=str(metrics.get('stepCount', 0)))
                self.passed_step_count_label.config(text=str(metrics.get('passedStepCount', 0)))
                self.failed_step_count_label.config(text=str(metrics.get('failedStepCount', 0)))
                self.coverage_percentage_label.config(text=f"{metrics.get('coveragePercentage', 0):.1f}%")
        except:
            self.reset_stats()

    def create_stat_boxes(self):
        # Stats layout - 2x2 grid
        stats = [
            ("Total Test Suites", "total_test_suites"),
            ("Total Test Cases", "total_test_cases"),
            ("Passed Cases", "total_passed_cases"),
            ("Failed Cases", "total_failed_cases")
        ]
        
        for i, (label, key) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            # Stat box container
            box_frame = tk.Frame(
                self.stats_frame,
                bg="#f8f9fa",
                padx=20,
                pady=15,
                relief="flat",
                borderwidth=1
            )
            box_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Configure grid weights
            self.stats_frame.grid_columnconfigure(col, weight=1)
            
            # Stat value
            value_label = tk.Label(
                box_frame,
                text="0",
                font=("Helvetica", 24, "bold"),
                bg="#f8f9fa"
            )
            value_label.pack()
            
            # Stat label
            tk.Label(
                box_frame,
                text=label,
                font=("Helvetica", 12),
                fg="#666666",
                bg="#f8f9fa"
            ).pack()
            
            # Store reference to value label
            setattr(self, f"{key}_label", value_label)

    def update_display(self, *args):
        current_project = self.state_manager.get_state('snapshots.current_project')
        current_date = self.state_manager.get_state('snapshots.current_date')
        current_snapshot = self.state_manager.get_state('snapshots.current_snapshot')

        print(f"Updating display with: {current_project}, {current_date}, {current_snapshot}")  # Debug log
        
        if not current_project:
            self.project_label.config(text="No Project Selected")
            self.date_label.config(text="")
            self.reset_stats()
            return
            
        # Update project and date labels
        self.project_label.config(text=current_project)
        self.date_label.config(text=current_date if current_date else "No date selected")
        
        # Update stats if we have a snapshot
        if current_project and current_date and current_snapshot:
            self.update_stats(current_project, current_date, current_snapshot)
        else:
            self.reset_stats()

    def reset_stats(self):
        # Reset status
        self.status_value.config(text="N/A", fg="#666666")
        
        # Reset all metric labels
        metrics = ['suite_count', 'case_count', 'passed_case_count', 'failed_case_count',
                  'step_count', 'passed_step_count', 'failed_step_count']
        
        for metric in metrics:
            label = getattr(self, f"{metric}_label")
            label.config(text="0")
        
        self.coverage_percentage_label.config(text="0.0%")