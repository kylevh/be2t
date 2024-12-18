import os
import json
from typing import List, Dict
from datetime import datetime
from utils.state_manager import StateManager

class SnapshotProcessor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.state_manager = StateManager()
        self.snapshot_dir = os.path.join(os.getcwd(), 'soap/snapshots')
        self.projects = set()
        self.dates = set()
        self._scan_snapshots()
        self._update_state()

    def _scan_snapshots(self) -> None:
        """Scan the snapshots directory and collect all projects and dates"""
        if not os.path.exists(self.snapshot_dir):
            print(f"Warning: Snapshots directory '{self.snapshot_dir}' does not exist")
            return

        for date_folder in os.listdir(self.snapshot_dir):
            date_path = os.path.join(self.snapshot_dir, date_folder)
            
            if not os.path.isdir(date_path) or not self._is_valid_date_folder(date_folder):
                continue

            self.dates.add(date_folder)
            
            for project_folder in os.listdir(date_path):
                project_path = os.path.join(date_path, project_folder)
                if os.path.isdir(project_path):
                    self.projects.add(project_folder)

    def _update_state(self) -> None:
        """Update the global state with snapshot information"""
        # RENABLE
        self.state_manager.set_state('snapshots.all_projects', sorted(list(self.projects)))
        self.state_manager.set_state('snapshots.all_dates', sorted(list(self.dates)))

        # self.state_manager.set_state('snapshots', {
        #     'all_projects': sorted(list(self.projects)),
        #     'all_dates': sorted(list(self.dates)),
        #     'current_project': None,
        #     'current_project_dates': [],
        #     'current_date': None,
        #     'current_snapshot': None
        # })

    def select_project(self, project_name: str, date: str = None) -> None:
        """Select a project and optionally set a specific date and its latest snapshot"""
        project_dates = self.get_project_dates(project_name)
        
        if date is None and project_dates:
            # If no date specified, use the latest date
            current_date = project_dates[-1]  # Dates are sorted, so last one is latest
            current_snapshot = self.get_latest_snapshot_for_date(project_name, current_date)
        else:
            # Only set date and snapshot if the date is valid for this project
            current_date = date if date in project_dates else None
            current_snapshot = None
            if current_date:
                current_snapshot = self.get_latest_snapshot_for_date(project_name, current_date)

        # REENABLE
        self.state_manager.set_state('snapshots.current_project', project_name)
        self.state_manager.set_state('snapshots.current_date', current_date)
        self.state_manager.set_state('snapshots.current_snapshot', current_snapshot)
        self.state_manager.set_state('snapshots.current_project_dates', project_dates)

    def _is_valid_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches YYYY-MM-DD format"""
        try:
            datetime.strptime(folder_name, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_all_projects(self) -> List[str]:
        """Return a sorted list of all unique project names"""
        return list(self.projects)

    def get_all_dates(self) -> List[str]:
        """Return a sorted list of all unique dates"""
        return list(self.dates)

    def get_project_dates(self, project: str) -> List[str]:
        """Get all dates that have snapshots for a specific project"""
        project_dates =[]
        for date_folder in self.dates:
            project_path = os.path.join(self.snapshot_dir, date_folder, project)
            if os.path.exists(project_path):
                project_dates.append(date_folder)
        return sorted(project_dates)
    
    def get_latest_snapshot_for_date(self, project_name: str, date: str) -> str:
        """Get the latest snapshot file directory for a specific project and date"""
        project_path = os.path.join(self.snapshot_dir, date, project_name)
        if not os.path.exists(project_path):
            return None
        snapshots = [f for f in os.listdir(project_path) if f.endswith('.json')]
        return sorted(snapshots)[-1]

    def get_latest_snapshot(self, project_name: str) -> tuple[str, str]:
        """Get the latest snapshot file across all dates for a specific project
        Returns: Tuple of (date, filename) or (None, None) if no snapshots found
        """
        # Get all dates for this project and sort them (newest first)
        project_dates = self.get_project_dates(project_name)
        if not project_dates:
            return None, None
            
        latest_date = project_dates[-1]  # Dates are already sorted by get_project_dates()
        latest_snapshot = self.get_latest_snapshot_for_date(project_name, latest_date)
        
        return latest_date, latest_snapshot

    def get_coverage_over_time_for_suite(self, project_name: str, test_suite_name: str, days: int = 30) -> Dict[str, float]:
        """Get coverage data for a specific test suite of a project over the specified number of days."""
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        # Initialize coverage data dictionary
        coverage_data = self._initialize_coverage_data(start_date, end_date)
        
        # Get all snapshots for this project within date range
        for date_str in self.dates:
            snapshot_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= snapshot_date <= end_date:
                project_path = os.path.join(self.snapshot_dir, date_str, project_name)
                if os.path.exists(project_path):
                    latest_snapshot = self.get_latest_snapshot_for_date(project_name, date_str)
                    if latest_snapshot:
                        coverage_data[date_str] = self._calculate_coverage_for_snapshot(project_path, latest_snapshot, test_suite_name)
        
        return coverage_data

    def _initialize_coverage_data(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Initialize a dictionary with dates as keys and 0.0 as default coverage values."""
        from datetime import timedelta
        
        coverage_data = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            coverage_data[date_str] = 0.0
            current_date += timedelta(days=1)
        
        return coverage_data

    def _calculate_coverage_for_snapshot(self, project_path: str, snapshot_filename: str, test_suite_name: str) -> float:
        """Calculate the coverage percentage for a given snapshot and test suite."""
        snapshot_path = os.path.join(project_path, snapshot_filename)
        try:
            with open(snapshot_path, 'r') as f:
                data = json.load(f)
                suite = self._find_test_suite(data, test_suite_name)
                if suite:
                    return self._compute_coverage_percentage(suite)
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error processing snapshot at {snapshot_path}: {str(e)}")
        
        return 0.0

    def _find_test_suite(self, data: dict, test_suite_name: str) -> dict:
        """Find and return the test suite with the given name from the snapshot data."""
        for suite in data.get('testSuites', []):
            if suite.get('testSuiteName') == test_suite_name:
                return suite
        return None

    def _compute_coverage_percentage(self, suite: dict) -> float:
        """Compute the coverage percentage for a given test suite."""
        total_enabled_steps = 0
        total_passed_steps = 0
        
        for test_case in suite.get('testCases', []):
            if test_case.get('disabled', False):
                continue  # Skip disabled test cases
            
            for step in test_case.get('testSteps', []):
                if step.get('disabled', False):
                    continue  # Skip disabled test steps
                
                total_enabled_steps += 1
                if step.get('statusCode') == 'passed':
                    total_passed_steps += 1
        
        if total_enabled_steps > 0:
            return round((total_passed_steps / total_enabled_steps) * 100, 2)
        
        return 0.0


if __name__ == "__main__":
    # Create processor instance
    processor = SnapshotProcessor()
    processor._scan_snapshots()
    print("all projects:", processor.get_all_projects())
    print("all dates:", processor.get_all_dates())

    print("project dates:", processor.get_project_dates("Sample Project"))
    print("latest snapshot:", processor.get_latest_snapshot("Sample Project"))
    print("coverage over time:", processor.get_coverage_over_time_for_suite("Sample Project", "DEV"))
