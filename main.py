"""
Main script for the trading system divergence detection.
Orchestrates the entire process in a single loop without threads.
"""
import pandas as pd
import time
from datetime import datetime
from divergence_detector import DivergenceDetector


def load_market_data():
    """
    Load OHLC data from parquet files.
    
    Returns:
        dict: Dictionary with symbol names as keys and DataFrames as values
    """
    symbols_data = {}
    
    try:
        # Load US100 data
        us100_df = pd.read_parquet('US100.cash.parquet')
        symbols_data['US100.cash'] = us100_df
        print(f"Loaded US100.cash: {len(us100_df)} records")
        
        # Load US500 data
        us500_df = pd.read_parquet('US500.cash.parquet')
        symbols_data['US500.cash'] = us500_df
        print(f"Loaded US500.cash: {len(us500_df)} records")
        
    except Exception as e:
        print(f"Error loading market data: {e}")
        
    return symbols_data


def display_detected_setups(setups_df):
    """
    Display detected setups in a formatted way.
    
    Args:
        setups_df (pd.DataFrame): DataFrame with detected setups
    """
    if setups_df.empty:
        print("No divergence setups detected.")
        return
    
    print(f"\n=== DETECTED SETUPS ({len(setups_df)}) ===")
    
    # Setup type mapping
    setup_types = {
        0: "Stochastic Divergence",
        1: "Correlated Pair Swing Failure", 
        2: "Correlated Pair Fake Breakout"
    }
    
    # Direction mapping
    directions = {0: "Bullish", 1: "Bearish"}
    
    # Session mapping
    sessions = {0: "London", 1: "NY_AM", 2: "NY_PM"}
    
    for _, setup in setups_df.iterrows():
        print(f"""
Symbol: {setup['Symbol']}
Timestamp: {setup['Timestamp']}
Session: {sessions.get(setup['Session'], 'Unknown')}
Direction: {directions.get(setup['Direction'], 'Unknown')}
Setup Type: {setup_types.get(setup['Setup Type'], 'Unknown')}
{'-' * 50}""")


def save_setups_to_file(setups_df, filename="detected_setups.csv"):
    """
    Save detected setups to a CSV file.
    
    Args:
        setups_df (pd.DataFrame): DataFrame with detected setups
        filename (str): Output filename
    """
    try:
        setups_df.to_csv(filename, index=False)
        print(f"Setups saved to {filename}")
    except Exception as e:
        print(f"Error saving setups: {e}")


def main():
    """
    Main execution loop.
    """
    print("=== Trading System Divergence Detection ===")
    print(f"Started at: {datetime.now()}")
    
    # Initialize the divergence detector
    detector = DivergenceDetector()
    
    # Load market data
    print("\nLoading market data...")
    symbols_data = load_market_data()
    
    if not symbols_data:
        print("No market data loaded. Exiting.")
        return
    
    # Main detection loop
    iteration = 0
    max_iterations = 5  # Limit iterations for demo purposes
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n=== ITERATION {iteration} ===")
        print(f"Timestamp: {datetime.now()}")
        
        try:
            # Scan for divergence patterns
            print("Scanning for divergence patterns...")
            detected_setups = detector.scan_for_divergences(symbols_data)
            
            # Display results
            display_detected_setups(detected_setups)
            
            # Save to file
            if not detected_setups.empty:
                save_setups_to_file(detected_setups, f"setups_iteration_{iteration}.csv")
            
            # Display detector statistics
            print(f"\nDetector Statistics:")
            print(f"Session data records: {len(detector.session_detector.active_session_df)}")
            print(f"Reference levels calculated: {len(detector.reference_levels_calculator.reference_levels_df)}")
            print(f"Total setups detected: {len(detected_setups)}")
            
        except Exception as e:
            print(f"Error in iteration {iteration}: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait before next iteration (in real implementation, this would be based on new data arrival)
        if iteration < max_iterations:
            print(f"\nWaiting 2 seconds before next iteration...")
            time.sleep(2)
    
    print(f"\n=== FINAL RESULTS ===")
    
    # Display final detected setups
    final_setups = detector.detected_setups_df
    display_detected_setups(final_setups)
    
    # Save final results
    if not final_setups.empty:
        save_setups_to_file(final_setups, "final_detected_setups.csv")
    
    print(f"\nTrading system completed at: {datetime.now()}")


if __name__ == "__main__":
    main()