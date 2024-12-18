from components.base_component import BaseComponent
import tkinter as tk
from tkinter import ttk
import json
import os
import csv

class SnapshotPage(BaseComponent):
    def create_widgets(self):
        # Subscribe to state changes
        self.state_manager.subscribe('snapshots.current_project', self.update_display)
        self.state_manager.subscribe('snapshots.current_date', self.update_display)
        self.state_manager.subscribe('snapshots.current_snapshot', self.update_display)

        # Create search frame at the top
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True)
        
        # Bind search update to entry changes
        self.search_var.trace('w', self.update_display)

        # Add download button to search frame
        download_button = ttk.Button(search_frame, text="Download CSV", command=self.export_to_csv)
        download_button.pack(side='right', padx=5)
        
        # Create table
        columns = ('ID', 'DEV Coverage', 'SAT Coverage', 'API', 'Functionality', 
                  'Method', 'Scenario', 'Data Methods', 'Notes', 'Description')
        
        column_widths = {
            'ID': 40,           # Narrow width for ID
            'DEV Coverage': 50,
            'SAT Coverage': 50,
            'API': 100,        # Wider for API paths
            'Functionality': 150,
            'Method': 60,      # Narrow for HTTP methods
            'Scenario': 150,
            'Data Methods': 120,
            'Notes': 150,
            'Description': 100
        }
        
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Configure style with modern look
        style = ttk.Style()
        style.configure('Treeview', 
                        rowheight=25, 
                        font=('Helvetica', 10), 
                        background='#f9f9f9', 
                        fieldbackground='#f9f9f9')
        style.configure('Treeview.Heading', 
                        font=('Helvetica', 11, 'bold'), 
                        background='#FFE5B4',  # Changed to a soft yellow color
                        relief='flat')
        # style.map('Treeview', 
        #           background=[('selected', '#ececec')])
        
        # Add tag configuration for alternating row colors
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('suite_header', background='#FFFF00', font=('Helvetica', 10, 'bold'))
        
        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])  # Adjust width as needed
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load and display data
        self.update_display()

    def update_display(self, *args):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get current state
        current_project = self.state_manager.get_state('snapshots.current_project')
        current_date = self.state_manager.get_state('snapshots.current_date')
        current_snapshot = self.state_manager.get_state('snapshots.current_snapshot')
        
        if not all([current_project, current_date, current_snapshot]):
            return
            
        # Process snapshot
        snapshot_path = os.path.join('soap', 'snapshots', current_date, current_project, current_snapshot)
        
        try:
            with open(snapshot_path) as f:
                data = json.load(f)
                self.process_snapshot_data(data)
        except Exception as e:
            print(f"Error loading snapshot data: {e}")
    
    def load_snapshot_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get latest snapshot file
        snapshot_dir = "soap/snapshots"
        latest_date = self.get_latest_date(snapshot_dir)
        if not latest_date:
            return
            
        # Process each project's snapshot
        step_id = 1
        for project_dir in os.listdir(os.path.join(snapshot_dir, latest_date)):
            latest_snapshot = self.get_latest_snapshot(os.path.join(snapshot_dir, latest_date, project_dir))
            if latest_snapshot:
                with open(latest_snapshot) as f:
                    data = json.load(f)
                    step_id = self.process_snapshot_data(data, step_id)

    def process_snapshot_data(self, data):
        step_id = 1
        search_text = self.search_var.get().lower()
        
        for suite in data['testSuites']:
            suite_items = []  # Keep track of items in this suite
            header_item = self.tree.insert('', 'end', values=(
                suite['testSuiteName'].upper(),
                '', '', '', '', '', '', '', '', ''
            ), tags=('suite_header',))
            
            is_dev = suite['testSuiteName'].upper() == 'DEV'
            is_sat = suite['testSuiteName'].upper() == 'SAT'
            
            for test_case in suite['testCases']:
                for step in test_case['testSteps']:
                    # Prepare the data for each step
                    test_status = 'DISABLED' if step.get('disabled', False) else (
                        'YES' if step.get('statusCode', '').lower() == 'passed' 
                        else 'NO' if step.get('statusCode', '').lower() == 'failed'
                        else '')
                    dev_coverage = test_status if is_dev else ''
                    sat_coverage = test_status if is_sat else ''
                    data_methods = []
                    
                    # Extract data methods if they exist
                    if 'dataPrep' in step:
                        data_methods.append('Data Prep')
                    if 'dataValidation' in step:
                        data_methods.append('Data Validation')
                    if 'dataCleanup' in step:
                        data_methods.append('Data Cleanup')
                    
                    # Create row values tuple
                    row_values = (
                        step_id,
                        test_status if is_dev else '',
                        test_status if is_sat else '',
                        step['resource'],
                        test_case['testCaseName'],
                        step['method'],
                        step['testStepName'],
                        ', '.join(data_methods),
                        step.get('notes', ''),
                        step.get('description', '')
                    )
                    
                    # Check if any value in the row contains the search text
                    if not search_text or any(
                        str(value).lower().find(search_text) != -1 
                        for value in row_values
                    ):
                        tag = 'evenrow' if step_id % 2 == 0 else 'oddrow'
                        self.tree.insert('', 'end', values=row_values, tags=(tag,))
                        suite_items.append(step_id)
                    
                    step_id += 1
            
            # Remove suite header if no items match the search
            if not suite_items and search_text:
                self.tree.delete(header_item)
        
        return step_id

    def get_latest_date(self, base_dir):
        if not os.path.exists(base_dir):
            return None
        dates = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        return max(dates) if dates else None

    def get_latest_snapshot(self, project_dir):
        if not os.path.exists(project_dir):
            return None
        snapshots = [f for f in os.listdir(project_dir) if f.endswith('.json')]
        return os.path.join(project_dir, max(snapshots)) if snapshots else None

    def export_to_csv(self):
        try:
            # Ask user where to save the file
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV File"
            )
            
            if not filename:  # If user cancels the save
                return
                
            # Get the column names
            columns = [self.tree.heading(col, 'text') for col in self.tree['columns']]
            
            # Open a file for writing
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write the column headers
                writer.writerow(columns)
                
                # Write the data rows
                for row_id in self.tree.get_children():
                    row = self.tree.item(row_id)['values']
                    writer.writerow(row)  # Removed the suite_header check to include all rows
                        
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Success", "File saved successfully!")
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while saving the file:\n{str(e)}")

    def destroy(self):
        # Unsubscribe from state changes
        self.state_manager.unsubscribe('snapshots.current_project', self.update_display)
        self.state_manager.unsubscribe('snapshots.current_date', self.update_display)
        self.state_manager.unsubscribe('snapshots.current_snapshot', self.update_display)
        super().destroy()