"""
Test script to verify divergence detection with manual setup creation.
"""
import pandas as pd
import numpy as np
from divergence_detector import DivergenceDetector


def test_divergence_detection():
    print("=== TESTING DIVERGENCE DETECTION ===")
    
    # Load data
    symbols_data = {
        'US100.cash': pd.read_parquet('US100.cash.parquet').tail(200),
        'US500.cash': pd.read_parquet('US500.cash.parquet').tail(200)
    }
    
    print(f"US100 data: {len(symbols_data['US100.cash'])} records")
    print(f"US500 data: {len(symbols_data['US500.cash'])} records")
    
    # Initialize detector
    detector = DivergenceDetector()
    
    # Scan for divergences
    print("\nScanning for divergences...")
    setups_df = detector.scan_for_divergences(symbols_data)
    
    print(f"Setups detected: {len(setups_df)}")
    
    if not setups_df.empty:
        print("Detected setups:")
        print(setups_df)
    else:
        print("No setups detected. Let's analyze why...")
        
        # Check the enhanced data
        enhanced_data = detector.prepare_data(symbols_data, max_records=200)
        
        for symbol, data in enhanced_data.items():
            print(f"\n{symbol} analysis:")
            swing_highs = data[data['SwingHigh'] == True]
            swing_lows = data[data['SwingLow'] == True]
            print(f"  Swing highs: {len(swing_highs)}")
            print(f"  Swing lows: {len(swing_lows)}")
            
            # Check stochastic range
            stoch_data = data.dropna(subset=['Stoch_K'])
            if len(stoch_data) > 0:
                print(f"  Stochastic K range: {stoch_data['Stoch_K'].min():.2f} - {stoch_data['Stoch_K'].max():.2f}")
            
            # Check reference levels vs price range
            ref_levels = detector.reference_levels_calculator.reference_levels_df
            if not ref_levels.empty:
                symbol_ref = ref_levels[ref_levels['Symbol'] == symbol]
                if not symbol_ref.empty:
                    symbol_ref = symbol_ref.iloc[0]
                    print(f"  Price range: {data['Low'].min():.2f} - {data['High'].max():.2f}")
                    print(f"  Support levels: {symbol_ref['Support_3']:.2f}, {symbol_ref['Support_2']:.2f}, {symbol_ref['Support_1']:.2f}")
                    print(f"  Resistance levels: {symbol_ref['Resistance_1']:.2f}, {symbol_ref['Resistance_2']:.2f}, {symbol_ref['Resistance_3']:.2f}")
                    
                    # Check if any prices broke levels
                    broke_support = (data['Low'] < symbol_ref['Support_1']).any()
                    broke_resistance = (data['High'] > symbol_ref['Resistance_1']).any()
                    print(f"  Broke support: {broke_support}")
                    print(f"  Broke resistance: {broke_resistance}")


def create_synthetic_test():
    """Create synthetic data with known divergence patterns for testing."""
    print("\n=== CREATING SYNTHETIC TEST DATA ===")
    
    # Create basic OHLC data
    dates = pd.date_range('2024-01-01', periods=50, freq='1min')
    
    # Create synthetic US100 data with deliberate divergence pattern
    base_price = 22000
    highs = []
    lows = []
    opens = []
    closes = []
    
    for i in range(50):
        # Create downward price trend with higher stochastic lows (bullish divergence)
        if i < 25:
            high = base_price - i * 2 + np.random.uniform(-5, 5)
            low = high - 20 + np.random.uniform(-5, 5)
        else:
            high = base_price - 25 * 2 - (i - 25) * 1 + np.random.uniform(-5, 5)
            low = high - 20 + np.random.uniform(-5, 5)
            
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
    
    print("Synthetic data created:")
    print(synthetic_df.head())
    print(f"Price range: {min(lows):.2f} - {max(highs):.2f}")
    
    # Test with synthetic data
    symbols_data = {'US100.cash': synthetic_df}
    
    detector = DivergenceDetector()
    setups_df = detector.scan_for_divergences(symbols_data)
    
    print(f"\nSynthetic test - Setups detected: {len(setups_df)}")
    if not setups_df.empty:
        print(setups_df)


if __name__ == "__main__":
    test_divergence_detection()
    create_synthetic_test()