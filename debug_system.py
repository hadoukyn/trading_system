"""
Debug script to test the individual components and see what's happening.
"""
import pandas as pd
import numpy as np
from session_detector import SessionDetector
from reference_levels_calculator import ReferenceLevelsCalculator
from swing_detector import detect_swing_highs_lows, calculate_stochastic


def debug_system():
    print("=== DEBUG TRADING SYSTEM ===")
    
    # Load small sample of data
    print("Loading sample data...")
    us100_df = pd.read_parquet('US100.cash.parquet').tail(100)
    us500_df = pd.read_parquet('US500.cash.parquet').tail(100)
    
    print(f"US100 sample: {len(us100_df)} records")
    print(f"US500 sample: {len(us500_df)} records")
    
    # Test session detector
    print("\n=== TESTING SESSION DETECTOR ===")
    session_detector = SessionDetector()
    session_df = session_detector.update_active_sessions(us100_df)
    print("Session distribution:")
    print(session_df['Session'].value_counts())
    print("Sample sessions:")
    print(session_df[['Timestamp', 'Session']].head(10))
    
    # Test reference levels calculator
    print("\n=== TESTING REFERENCE LEVELS ===")
    ref_calc = ReferenceLevelsCalculator()
    symbols_data = {'US100.cash': us100_df, 'US500.cash': us500_df}
    ref_levels = ref_calc.calculate_reference_levels(symbols_data)
    print("Reference levels:")
    print(ref_levels)
    
    # Test swing detection
    print("\n=== TESTING SWING DETECTION ===")
    us100_with_swings = detect_swing_highs_lows(us100_df)
    swing_highs = us100_with_swings[us100_with_swings['SwingHigh'] == True]
    swing_lows = us100_with_swings[us100_with_swings['SwingLow'] == True]
    print(f"Swing highs detected: {len(swing_highs)}")
    print(f"Swing lows detected: {len(swing_lows)}")
    
    if len(swing_highs) > 0:
        print("Sample swing highs:")
        print(swing_highs[['Timestamp', 'SwingHighPrice']].head(3))
    
    if len(swing_lows) > 0:
        print("Sample swing lows:")
        print(swing_lows[['Timestamp', 'SwingLowPrice']].head(3))
    
    # Test stochastic calculation
    print("\n=== TESTING STOCHASTIC INDICATOR ===")
    us100_with_stoch = calculate_stochastic(us100_with_swings)
    print("Stochastic data (last 5 records):")
    print(us100_with_stoch[['Timestamp', 'Close', 'Stoch_K', 'Stoch_D']].tail())
    
    # Test reference level breakouts
    print("\n=== TESTING REFERENCE LEVEL BREAKOUTS ===")
    last_candle = us100_df.iloc[-1]
    print(f"Last candle - High: {last_candle['High']}, Low: {last_candle['Low']}")
    
    # Check breakouts
    breakout_below = ref_calc.get_reference_level_for_breakout('US100.cash', last_candle['Low'], 'below')
    breakout_above = ref_calc.get_reference_level_for_breakout('US100.cash', last_candle['High'], 'above')
    
    print(f"Breakout below reference level: {breakout_below}")
    print(f"Breakout above reference level: {breakout_above}")
    
    # Show price ranges
    print(f"\nPrice ranges for US100:")
    print(f"Min Low: {us100_df['Low'].min()}")
    print(f"Max High: {us100_df['High'].max()}")
    print(f"Current Close: {last_candle['Close']}")


if __name__ == "__main__":
    debug_system()