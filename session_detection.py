"""
Session Detection Script for Trading System

This script determines the current trading session based on timestamps from Parquet database files.
It reads the most recent timestamp from OHLC data and classifies it into one of four trading sessions:
- Asia: 03:00 - 07:00
- London: 09:00 - 12:00  
- NY_AM: 14:00 - 18:00
- NY_PM: 21:00 - 23:00

The script can be imported by other scripts or executed directly.
"""

import pandas as pd
import glob
import os
from datetime import datetime
from typing import Tuple, Optional


def get_most_recent_timestamp() -> Optional[datetime]:
    """
    Read the most recent timestamp from all Parquet files in the current directory.
    
    Returns:
        datetime: The most recent timestamp found across all Parquet files
        None: If no Parquet files are found or if there's an error reading them
    """
    try:
        # Find all Parquet files in the current directory
        parquet_files = glob.glob("*.parquet")
        
        if not parquet_files:
            print("Warning: No Parquet files found in current directory")
            return None
        
        most_recent = None
        
        for file in parquet_files:
            try:
                # Read the Parquet file
                df = pd.read_parquet(file)
                
                # Combine Date and Timestamp columns to create full datetime
                df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Timestamp'])
                
                # Get the most recent timestamp from this file
                file_latest = df['DateTime'].max()
                
                # Keep track of the overall most recent timestamp
                if most_recent is None or file_latest > most_recent:
                    most_recent = file_latest
                    
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        return most_recent
        
    except Exception as e:
        print(f"Error in get_most_recent_timestamp(): {e}")
        return None


def determine_session(timestamp: datetime) -> str:
    """
    Determine the trading session based on the hour of the timestamp.
    
    Args:
        timestamp: The datetime to classify
        
    Returns:
        str: The session name ('Asia', 'London', 'NY_AM', 'NY_PM', or 'Closed')
    """
    hour = timestamp.hour
    
    # Define session hours (24-hour format)
    if 3 <= hour < 7:
        return "Asia"
    elif 9 <= hour < 12:
        return "London"
    elif 14 <= hour < 18:
        return "NY_AM"
    elif 21 <= hour < 23:
        return "NY_PM"
    else:
        return "Closed"


def get_current_session() -> Tuple[Optional[datetime], str]:
    """
    Get the current trading session based on the most recent timestamp in Parquet files.
    
    Returns:
        Tuple[datetime, str]: A tuple containing the timestamp and session name
    """
    timestamp = get_most_recent_timestamp()
    
    if timestamp is None:
        return None, "Unknown"
    
    session = determine_session(timestamp)
    return timestamp, session


def create_session_dataframe(timestamp: datetime, session: str) -> pd.DataFrame:
    """
    Create a DataFrame containing the current session information.
    
    Args:
        timestamp: The timestamp used for session determination
        session: The determined session name
        
    Returns:
        pd.DataFrame: DataFrame with timestamp and session information
    """
    return pd.DataFrame({
        'Timestamp': [timestamp],
        'Session': [session]
    })


def main():
    """
    Main function to demonstrate session detection functionality.
    Prints the current session information to console.
    """
    print("Trading Session Detection")
    print("=" * 40)
    
    timestamp, session = get_current_session()
    
    if timestamp is None:
        print("Error: Could not determine current session")
        print("Reason: Unable to read timestamp from Parquet files")
        return
    
    # Create DataFrame for potential use by other scripts
    session_df = create_session_dataframe(timestamp, session)
    
    # Display results
    print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Session: {session}")
    
    # Show session DataFrame
    print("\nSession DataFrame:")
    print(session_df.to_string(index=False))
    
    return session_df


if __name__ == "__main__":
    main()