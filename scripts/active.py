import ctypes
import random
import time
import threading

def prevent_sleep():
    """Prevent computer from sleeping."""
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED

def simulate_activity():
    """Simulate system activity to keep computer and Teams active."""
    while True:
        current_hour = time.localtime().tm_hour
        # Check if the current time is between 6 AM and 3 PM, excluding 10 AM to 11 AM
        if (6 <= current_hour < 10) or (11 <= current_hour < 15):
            # Windows-specific method to trigger system activity
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Left Windows key press
            ctypes.windll.user32.keybd_event(0x5B, 0, 0x0002, 0)  # Left Windows key release
        
        time.sleep(random.randint(240, 600))  # Random interval between 4-10 minutes
def main():
    prevent_sleep()
    activity_thread = threading.Thread(target=simulate_activity, daemon=True)
    activity_thread.start()
    
    try:
        while True:
            time.sleep(3600)  # Keep script running
    except KeyboardInterrupt:
        print("Script stopped.")

if __name__ == "__main__":
    main()