from components.base_component import BaseComponent
import tkinter as tk
from datetime import datetime, timedelta

class AnalysisPage(BaseComponent):
    def create_widgets(self):
        # Subscribe to project changes
        self.state_manager.subscribe('snapshots.current_project', self.update_graph)
        
        # Main container
        self.main_container = tk.Frame(self, bg="#ffffff")
        self.main_container.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Graph title
        self.title_label = tk.Label(
            self.main_container,
            text="Backend Test Coverage (Last 30 Days)",
            font=("Helvetica", 16, "bold"),
            bg="#ffffff"
        )
        self.title_label.pack(pady=(5, 20))
        
        # Canvas for graph
        self.canvas_height = 400
        self.canvas_width = 800
        self.canvas = tk.Canvas(
            self.main_container,
            height=self.canvas_height,
            width=self.canvas_width,
            bg="white",
            bd=1,
            relief="solid"
        )
        self.canvas.pack(pady=20)

        # Add tooltip label
        self.tooltip = tk.Label(
            self.canvas,
            bg='#ffffe0',
            relief='solid',
            borderwidth=1,
            font=('Helvetica', 10)
        )
        
        # Initial graph
        self.update_graph()
        
    def update_graph(self, *args):
        self.canvas.delete("all")  # Clear canvas
        
        # Get current project
        current_project = self.state_manager.get_state('snapshots.current_project')
        if not current_project:
            self.draw_no_data()
            return
            
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29)
        
        # Remove the date range calculation since we'll use actual data points
        coverage_data = self.get_coverage_data(current_project, None, None)
        if not coverage_data:
            self.draw_no_data()
            return

        self.draw_graph(coverage_data)
        
    def get_coverage_data(self, project, start_date, end_date):
        return self.snapshot_processor.get_coverage_over_time(project)
        
    def draw_graph(self, coverage_data):
        # Graph dimensions
        padding = 50
        graph_width = self.canvas_width - (padding * 2)
        graph_height = self.canvas_height - (padding * 2)

        # Filter out days with 0 coverage and get sorted dates
        valid_dates = sorted([date for date, coverage in coverage_data.items() if coverage > 0])
        if not valid_dates:
            self.draw_no_data()
            return
        
        # Draw axes
        self.canvas.create_line(
            padding, self.canvas_height - padding,
            padding, padding,
            width=2
        )
        self.canvas.create_line(
            padding, self.canvas_height - padding,
            self.canvas_width - padding, self.canvas_height - padding,
            width=2
        )
        
        # Draw Y-axis labels (0% to 100%)
        for i in range(0, 101, 20):
            y = self.canvas_height - padding - (i / 100 * graph_height)
            self.canvas.create_text(padding - 20, y, text=f"{i}%")
            # Draw horizontal grid lines
            self.canvas.create_line(
                padding, y,
                self.canvas_width - padding, y,
                dash=(2, 4),
                fill="#cccccc"
            )
        
       # Plot data points
        points = []
        for i, date in enumerate(valid_dates):
            x = padding + (i / (len(valid_dates) - 1 if len(valid_dates) > 1 else 1) * graph_width)
            y = self.canvas_height - padding - (coverage_data[date] / 100 * graph_height)
            points.append((x, y))

            # Draw point and bind hover events
            point_id = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#007bff", tags=f"point_{i}")
            self.canvas.tag_bind(f"point_{i}", '<Enter>', 
                lambda e, date=date, coverage=coverage_data[date], x=x, y=y: 
                self.show_tooltip(e, date, coverage, x, y))
            self.canvas.tag_bind(f"point_{i}", '<Leave>', self.hide_tooltip)
            
            # Draw date label (adjust frequency based on number of points)
            label_frequency = max(1, len(valid_dates) // 6)  # Show ~6 labels
            if i % label_frequency == 0:
                self.canvas.create_text(
                    x, self.canvas_height - padding + 20,
                    text=date[5:],  # Show only MM-DD
                    angle=45
                )
        
        # Update title based on date range
        if len(valid_dates) > 0:
            date_range = f"({valid_dates[0]} to {valid_dates[-1]})"
            self.title_label.config(text=f"Backend Test Coverage {date_range}")
        
        # Draw lines between points
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="#007bff", width=2)

    def show_tooltip(self, event, date, coverage, x, y):
        self.tooltip.config(text=f"Date: {date}\nCoverage: {coverage:.1f}%")
        # Position tooltip above the point
        self.tooltip.place(x=x + 10, y=y - 30)
        
    def hide_tooltip(self, event):
        self.tooltip.place_forget()
            
    def draw_no_data(self):
        self.canvas.create_text(
            self.canvas_width / 2,
            self.canvas_height / 2,
            text="No data available\nPlease select a project",
            font=("Helvetica", 14),
            justify="center"
        )

    def destroy(self):
        self.state_manager.unsubscribe('snapshots.current_project', self.update_graph)
        super().destroy()