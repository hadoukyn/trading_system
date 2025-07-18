"""
Example usage of the divergence detection system.
This script shows how to use the system components individually and together.
"""
import pandas as pd
from divergence_detector import DivergenceDetector
from session_detector import SessionDetector
from reference_levels_calculator import ReferenceLevelsCalculator
from swing_detector import detect_swing_highs_lows, calculate_stochastic


def example_basic_usage():
    """Basic usage example."""
    print("=== BASIC USAGE EXAMPLE ===")
    
    # Load OHLC data
    symbols_data = {
        'US100.cash': pd.read_parquet('US100.cash.parquet').tail(1000),
        'US500.cash': pd.read_parquet('US500.cash.parquet').tail(1000)
    }
    
    # Initialize detector
    detector = DivergenceDetector()
    
    # Scan for divergences
    setups_df = detector.scan_for_divergences(symbols_data)
    
    print(f"Detected {len(setups_df)} divergence setups")
    
    if not setups_df.empty:
        # Define mappings for readable output
        setup_types = {
            0: "Stochastic Divergence",
            1: "Correlated Pair Swing Failure", 
            2: "Correlated Pair Fake Breakout"
        }
        directions = {0: "Bullish", 1: "Bearish"}
        sessions = {0: "London", 1: "NY_AM", 2: "NY_PM"}
        
        print("\nDetected Setups:")
        for _, setup in setups_df.iterrows():
            print(f"- {setup['Symbol']} at {setup['Timestamp']}")
            print(f"  Session: {sessions[setup['Session']]}")
            print(f"  Direction: {directions[setup['Direction']]}")
            print(f"  Type: {setup_types[setup['Setup Type']]}")
            print()


def example_individual_components():
    """Example of using individual components."""
    print("\n=== INDIVIDUAL COMPONENTS EXAMPLE ===")
    
    # Load sample data
    us100_df = pd.read_parquet('US100.cash.parquet').tail(200)
    
    # 1. Session Detection
    print("1. Session Detection:")
    session_detector = SessionDetector()
    session_df = session_detector.update_active_sessions(us100_df)
    print(f"Session distribution: {session_df['Session'].value_counts().to_dict()}")
    
    # 2. Reference Levels
    print("\n2. Reference Levels:")
    ref_calculator = ReferenceLevelsCalculator()
    symbols_data = {'US100.cash': us100_df}
    ref_levels = ref_calculator.calculate_reference_levels(symbols_data)
    print(f"Support levels: {ref_levels.iloc[0]['Support_1']:.2f}, {ref_levels.iloc[0]['Support_2']:.2f}, {ref_levels.iloc[0]['Support_3']:.2f}")
    print(f"Resistance levels: {ref_levels.iloc[0]['Resistance_1']:.2f}, {ref_levels.iloc[0]['Resistance_2']:.2f}, {ref_levels.iloc[0]['Resistance_3']:.2f}")
    
    # 3. Swing Detection
    print("\n3. Swing Detection:")
    us100_with_swings = detect_swing_highs_lows(us100_df)
    swing_highs = us100_with_swings[us100_with_swings['SwingHigh'] == True]
    swing_lows = us100_with_swings[us100_with_swings['SwingLow'] == True]
    print(f"Swing highs detected: {len(swing_highs)}")
    print(f"Swing lows detected: {len(swing_lows)}")
    
    # 4. Stochastic Calculation
    print("\n4. Stochastic Indicator:")
    us100_with_stoch = calculate_stochastic(us100_with_swings)
    stoch_data = us100_with_stoch.dropna(subset=['Stoch_K'])
    print(f"Stochastic K range: {stoch_data['Stoch_K'].min():.2f} - {stoch_data['Stoch_K'].max():.2f}")
    print(f"Latest Stochastic K: {stoch_data['Stoch_K'].iloc[-1]:.2f}")


def example_synthetic_data():
    """Example with synthetic data that should produce divergences."""
    print("\n=== SYNTHETIC DATA EXAMPLE ===")
    
    # Create synthetic data with known divergence pattern
    import numpy as np
    
    # Create downward price trend with higher stochastic lows (bullish divergence)
    dates = pd.date_range('2024-01-01', periods=50, freq='1min')
    base_price = 22000
    
    highs = []
    lows = []
    opens = []
    closes = []
    
    for i in range(50):
        # Create gradual downtrend
        high = base_price - i * 2 + np.random.uniform(-3, 3)
        low = high - 15 + np.random.uniform(-3, 3)
        open_price = low + np.random.uniform(0, high - low)
        close = low + np.random.uniform(0, high - low)
        
        highs.append(round(high, 2))
        lows.append(round(low, 2))
        opens.append(round(open_price, 2))
        closes.append(round(close, 2))
    
    synthetic_df = pd.DataFrame({
        'Date': [d.strftime('%Y.%m.%d') for d in dates],
        'Timestamp': [d.strftime('%H:%M') for d in dates],
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes
    })
    
    print(f"Created synthetic data with {len(synthetic_df)} records")
    print(f"Price range: {min(lows):.2f} - {max(highs):.2f}")
    
    # Test divergence detection
    symbols_data = {'US100.cash': synthetic_df}
    detector = DivergenceDetector()
    setups_df = detector.scan_for_divergences(symbols_data)
    
    print(f"Synthetic data divergences detected: {len(setups_df)}")
    if not setups_df.empty:
        print(setups_df[['Symbol', 'Timestamp', 'Direction', 'Setup Type']])


if __name__ == "__main__":
    try:
        example_basic_usage()
        example_individual_components()
        example_synthetic_data()
        
        print("\n=== EXAMPLE COMPLETED SUCCESSFULLY ===")
        print("All components are working correctly!")
        
    except Exception as e:
        print(f"Error in example: {e}")
        import traceback
        traceback.print_exc()