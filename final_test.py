"""
Final comprehensive test of the divergence detection system.
"""
import pandas as pd
from divergence_detector import DivergenceDetector


def comprehensive_test():
    print("=== COMPREHENSIVE DIVERGENCE DETECTION TEST ===")
    
    # Load larger sample for better detection
    print("Loading data...")
    us100_df = pd.read_parquet('US100.cash.parquet').tail(2000)  # Last 2000 records
    us500_df = pd.read_parquet('US500.cash.parquet').tail(2000)
    
    symbols_data = {
        'US100.cash': us100_df,
        'US500.cash': us500_df
    }
    
    print(f"US100 data: {len(us100_df)} records")
    print(f"US500 data: {len(us500_df)} records")
    print(f"US100 time range: {us100_df['Timestamp'].iloc[0]} to {us100_df['Timestamp'].iloc[-1]}")
    
    # Initialize detector
    detector = DivergenceDetector()
    
    # Test with different data sizes
    for data_size in [500, 1000, 2000]:
        print(f"\n--- Testing with {data_size} records ---")
        
        test_data = {
            'US100.cash': us100_df.tail(data_size),
            'US500.cash': us500_df.tail(data_size)
        }
        
        # Scan for divergences
        setups_df = detector.scan_for_divergences(test_data)
        
        print(f"Setups detected: {len(setups_df)}")
        
        if not setups_df.empty:
            print("Detected setups:")
            setup_types = {0: "Stochastic Divergence", 1: "Correlated Pair Swing Failure", 2: "Correlated Pair Fake Breakout"}
            directions = {0: "Bullish", 1: "Bearish"}
            sessions = {0: "London", 1: "NY_AM", 2: "NY_PM"}
            
            for _, setup in setups_df.iterrows():
                print(f"  {setup['Symbol']} | {setup['Timestamp']} | {sessions[setup['Session']]} | {directions[setup['Direction']]} | {setup_types[setup['Setup Type']]}")
        
        # Show some statistics
        enhanced_data = detector.prepare_data(test_data, max_records=data_size)
        for symbol, data in enhanced_data.items():
            swing_highs = data[data['SwingHigh'] == True]
            swing_lows = data[data['SwingLow'] == True]
            print(f"  {symbol}: {len(swing_highs)} swing highs, {len(swing_lows)} swing lows")
    
    print(f"\n=== REFERENCE LEVELS ANALYSIS ===")
    ref_levels = detector.reference_levels_calculator.reference_levels_df
    print(ref_levels)
    
    print(f"\n=== SESSION DISTRIBUTION ===")
    sessions_df = detector.session_detector.active_session_df
    if not sessions_df.empty:
        print(sessions_df['Session'].value_counts())


if __name__ == "__main__":
    comprehensive_test()