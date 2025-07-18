"""
Detailed debug script to understand why divergence detection is not working.
"""
import pandas as pd
import numpy as np
from divergence_detector import DivergenceDetector
from swing_detector import find_recent_swings, detect_divergence


def detailed_debug():
    print("=== DETAILED DIVERGENCE DEBUG ===")
    
    # Load larger sample for better swing detection
    us100_df = pd.read_parquet('US100.cash.parquet').tail(500)
    symbols_data = {'US100.cash': us100_df}
    
    detector = DivergenceDetector()
    
    # Prepare enhanced data
    enhanced_data = detector.prepare_data(symbols_data, max_records=500)
    us100_enhanced = enhanced_data['US100.cash']
    
    # Get session and reference data
    session_df = detector.session_detector.update_active_sessions(us100_df.tail(500))
    reference_levels = detector.reference_levels_calculator.calculate_reference_levels(enhanced_data)
    
    print("Reference levels:")
    print(reference_levels)
    
    # Check swing detection first
    swing_highs = us100_enhanced[us100_enhanced['SwingHigh'] == True]
    swing_lows = us100_enhanced[us100_enhanced['SwingLow'] == True]
    print(f"\nTotal swing highs detected: {len(swing_highs)}")
    print(f"Total swing lows detected: {len(swing_lows)}")
    
    if len(swing_highs) > 0:
        print("Recent swing highs:")
        print(swing_highs[['Timestamp', 'SwingHighPrice', 'Stoch_K']].tail(5))
    
    if len(swing_lows) > 0:
        print("Recent swing lows:")
        print(swing_lows[['Timestamp', 'SwingLowPrice', 'Stoch_K']].tail(5))
    
    # Manually check a few candles for breakouts and swings
    print(f"\nAnalyzing last 10 candles...")
    
    # Use larger window and don't reset index to preserve swing detection
    recent_data = us100_enhanced.tail(200).copy()  # Keep original index
    recent_data_reset = recent_data.reset_index(drop=True)  # Reset for analysis
    
    # Check only last 5 candles for debugging
    for i in range(195, len(recent_data_reset)):
        candle = recent_data_reset.iloc[i]
        print(f"\nCandle {i} - Timestamp: {candle['Timestamp']}")
        print(f"  OHLC: {candle['Open']:.2f}, {candle['High']:.2f}, {candle['Low']:.2f}, {candle['Close']:.2f}")
        print(f"  Stochastic K: {candle['Stoch_K']:.2f}")
        
        # Check breakouts
        ref_below = detector.reference_levels_calculator.get_reference_level_for_breakout(
            'US100.cash', candle['Low'], 'below'
        )
        ref_above = detector.reference_levels_calculator.get_reference_level_for_breakout(
            'US100.cash', candle['High'], 'above'
        )
        
        print(f"  Reference level breakout below: {ref_below}")
        print(f"  Reference level breakout above: {ref_above}")
        
        if ref_below is not None or ref_above is not None:
            # Check swings
            if ref_below is not None:
                print(f"  BULLISH SETUP POTENTIAL:")
                swing_lows = find_recent_swings(recent_data_reset, i, 'low', max_lookback=50)
                print(f"    Swing lows found: {len(swing_lows)}")
                
                for j, (idx, price) in enumerate(swing_lows):
                    if idx < len(recent_data_reset):
                        stoch_val = recent_data_reset.iloc[idx]['Stoch_K']
                        print(f"      Swing {j}: Index {idx}, Price {price:.2f}, Stoch {stoch_val:.2f}")
                
                if len(swing_lows) >= 2:
                    stoch_values = [recent_data_reset.iloc[idx]['Stoch_K'] for idx, _ in swing_lows if idx < len(recent_data_reset)]
                    if len(stoch_values) >= 2:
                        is_divergence = detect_divergence(swing_lows, stoch_values, 'bullish')
                        print(f"    Bullish divergence detected: {is_divergence}")
            
            if ref_above is not None:
                print(f"  BEARISH SETUP POTENTIAL:")
                swing_highs = find_recent_swings(recent_data_reset, i, 'high', max_lookback=50)
                print(f"    Swing highs found: {len(swing_highs)}")
                
                for j, (idx, price) in enumerate(swing_highs):
                    if idx < len(recent_data_reset):
                        stoch_val = recent_data_reset.iloc[idx]['Stoch_K']
                        print(f"      Swing {j}: Index {idx}, Price {price:.2f}, Stoch {stoch_val:.2f}")
                
                if len(swing_highs) >= 2:
                    stoch_values = [recent_data_reset.iloc[idx]['Stoch_K'] for idx, _ in swing_highs if idx < len(recent_data_reset)]
                    if len(stoch_values) >= 2:
                        is_divergence = detect_divergence(swing_highs, stoch_values, 'bearish')
                        print(f"    Bearish divergence detected: {is_divergence}")
                        
                        # Show detailed divergence analysis
                        if len(swing_highs) >= 2:
                            swing1_price = swing_highs[1][1]  # Older swing  
                            swing2_price = swing_highs[0][1]  # Newer swing
                            stoch1 = stoch_values[1]  # Older stochastic
                            stoch2 = stoch_values[0]  # Newer stochastic
                            
                            price_higher_high = swing2_price > swing1_price
                            stoch_lower_high = stoch2 < stoch1
                            
                            print(f"      Price higher high: {price_higher_high} ({swing2_price:.2f} > {swing1_price:.2f})")
                            print(f"      Stoch lower high: {stoch_lower_high} ({stoch2:.2f} < {stoch1:.2f})")
    
    # Now test the full detection
    print(f"\n=== RUNNING FULL DETECTION ===")
    setups_df = detector.scan_for_divergences(symbols_data)
    print(f"Setups detected: {len(setups_df)}")
    if not setups_df.empty:
        print(setups_df)


if __name__ == "__main__":
    detailed_debug()