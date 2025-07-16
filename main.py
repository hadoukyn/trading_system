"""
Main Runner Script for Trading System

This script continuously runs session detection every minute to provide real-time
session monitoring. It imports and uses the session_detection module.

Usage:
    python main.py

The script will run indefinitely, updating session information every 60 seconds.
Press Ctrl+C to stop execution.
"""

import time
import signal
import sys
from datetime import datetime
from session_detection import get_current_session, create_session_dataframe


class SessionMonitor:
    """
    Continuous session monitoring class that runs session detection every minute.
    """
    
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def run_session_detection(self):
        """
        Run a single session detection cycle and display results.
        
        Returns:
            bool: True if successful, False if there was an error
        """
        try:
            timestamp, session = get_current_session()
            
            if timestamp is None:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Could not determine session")
                return False
            
            # Create session DataFrame for potential use by other components
            session_df = create_session_dataframe(timestamp, session)
            
            # Display current session information
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                  f"Active Session: {session}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}")
            return False
    
    def run(self):
        """
        Main execution loop that runs session detection every minute.
        """
        print("Trading System - Session Monitor")
        print("=" * 50)
        print("Starting continuous session detection (every 60 seconds)")
        print("Press Ctrl+C to stop\n")
        
        # Run initial detection
        self.run_session_detection()
        
        # Main monitoring loop
        while self.running:
            try:
                # Wait for 60 seconds
                time.sleep(60)
                
                if self.running:  # Check if we're still supposed to be running
                    self.run_session_detection()
                    
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received. Stopping...")
                break
            except Exception as e:
                print(f"Unexpected error in main loop: {e}")
                time.sleep(5)  # Wait a bit before retrying
        
        print("Session monitoring stopped.")


def main():
    """
    Main function to start the session monitoring system.
    """
    monitor = SessionMonitor()
    monitor.run()


if __name__ == "__main__":
    main()