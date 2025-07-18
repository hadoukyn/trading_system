"""
SessionDetector class for detecting active trading sessions.
Sessions: 0 = London, 1 = NY_AM, 2 = NY_PM
"""
import pandas as pd
from datetime import datetime, time


class SessionDetector:
    def __init__(self):
        self.active_session_df = pd.DataFrame()
        
    def detect_session(self, timestamp_str):
        """
        Detect active session based on timestamp.
        
        Args:
            timestamp_str (str): Timestamp in format "HH:MM"
            
        Returns:
            int: Session ID (0=London, 1=NY_AM, 2=NY_PM)
        """
        # Parse timestamp to time object
        hour, minute = map(int, timestamp_str.split(':'))
        current_time = time(hour, minute)
        
        # Define session times (UTC)
        london_start = time(8, 0)   # 08:00 UTC
        london_end = time(16, 0)    # 16:00 UTC
        ny_am_start = time(13, 0)   # 13:00 UTC (overlaps with London)
        ny_am_end = time(17, 0)     # 17:00 UTC  
        ny_pm_start = time(17, 0)   # 17:00 UTC
        ny_pm_end = time(22, 0)     # 22:00 UTC
        
        # Session detection logic
        if london_start <= current_time < ny_am_start:
            return 0  # London only
        elif ny_am_start <= current_time < ny_pm_start:
            return 1  # NY_AM (overlaps with London)
        elif ny_pm_start <= current_time < ny_pm_end:
            return 2  # NY_PM
        else:
            return 0  # Default to London for other times
    
    def update_active_sessions(self, data_df):
        """
        Update active_session_df with session information for all timestamps.
        
        Args:
            data_df (pd.DataFrame): DataFrame with 'Timestamp' column
        """
        # Create a copy to avoid modifying original data
        session_data = data_df[['Date', 'Timestamp']].copy()
        
        # Detect session for each timestamp
        session_data['Session'] = session_data['Timestamp'].apply(self.detect_session)
        
        # Store in active_session_df
        self.active_session_df = session_data
        
        return self.active_session_df