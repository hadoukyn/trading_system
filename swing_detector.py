"""
Utility functions for swing high/low detection and technical indicators.
"""
import pandas as pd
import numpy as np


def detect_swing_highs_lows(data_df, swing_length=3):
    """
    Detect swing highs and lows using a 3-consecutive-candle pattern (reduced from 5 for better detection).
    
    Args:
        data_df (pd.DataFrame): OHLC data
        swing_length (int): Number of candles to check (default 3, reduced from 5)
        
    Returns:
        pd.DataFrame: DataFrame with SwingHigh and SwingLow columns
    """
    df = data_df.copy()
    df['SwingHigh'] = False
    df['SwingLow'] = False
    df['SwingHighPrice'] = np.nan
    df['SwingLowPrice'] = np.nan
    
    # Need at least swing_length candles on each side
    for i in range(swing_length, len(df) - swing_length):
        # Check for swing high
        current_high = df['High'].iloc[i]
        left_highs = df['High'].iloc[i-swing_length:i]
        right_highs = df['High'].iloc[i+1:i+swing_length+1]
        
        if (current_high > left_highs.max()) and (current_high > right_highs.max()):
            df.loc[df.index[i], 'SwingHigh'] = True
            df.loc[df.index[i], 'SwingHighPrice'] = round(current_high, 2)
        
        # Check for swing low
        current_low = df['Low'].iloc[i]
        left_lows = df['Low'].iloc[i-swing_length:i]
        right_lows = df['Low'].iloc[i+1:i+swing_length+1]
        
        if (current_low < left_lows.min()) and (current_low < right_lows.min()):
            df.loc[df.index[i], 'SwingLow'] = True
            df.loc[df.index[i], 'SwingLowPrice'] = round(current_low, 2)
    
    return df


def calculate_stochastic(data_df, k_period=3, d_period=3, smooth_k=3):
    """
    Calculate Stochastic Oscillator with given parameters.
    
    Args:
        data_df (pd.DataFrame): OHLC data
        k_period (int): %K period
        d_period (int): %D period  
        smooth_k (int): %K smoothing period
        
    Returns:
        pd.DataFrame: DataFrame with Stoch_K and Stoch_D columns
    """
    df = data_df.copy()
    
    # Calculate raw %K
    lowest_low = df['Low'].rolling(window=k_period).min()
    highest_high = df['High'].rolling(window=k_period).max()
    
    raw_k = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
    
    # Smooth %K
    df['Stoch_K'] = raw_k.rolling(window=smooth_k).mean()
    
    # Calculate %D (smoothed %K)
    df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()
    
    # Round to 2 decimal places
    df['Stoch_K'] = df['Stoch_K'].round(2)
    df['Stoch_D'] = df['Stoch_D'].round(2)
    
    return df


def find_recent_swings(df, current_idx, swing_type='high', max_lookback=50):
    """
    Find the most recent swing highs or lows from a given position.
    
    Args:
        df (pd.DataFrame): DataFrame with swing data
        current_idx (int): Current position index
        swing_type (str): 'high' or 'low'
        max_lookback (int): Maximum periods to look back
        
    Returns:
        list: List of (index, price) tuples for recent swings
    """
    swings = []
    
    if swing_type == 'high':
        swing_col = 'SwingHigh'
        price_col = 'SwingHighPrice'
    else:
        swing_col = 'SwingLow' 
        price_col = 'SwingLowPrice'
    
    # Look back from current position
    start_idx = max(0, current_idx - max_lookback)
    
    for i in range(current_idx - 1, start_idx - 1, -1):
        if i < len(df) and df.iloc[i][swing_col]:
            price = df.iloc[i][price_col]
            swings.append((i, price))
            
            # Stop after finding 2 swings for divergence analysis
            if len(swings) >= 2:
                break
    
    return swings


def detect_divergence(swings, stoch_values, divergence_type='bullish'):
    """
    Detect divergence between price swings and stochastic values.
    
    Args:
        swings (list): List of (index, price) tuples
        stoch_values (list): Corresponding stochastic values
        divergence_type (str): 'bullish' or 'bearish'
        
    Returns:
        bool: True if divergence is detected
    """
    if len(swings) < 2 or len(stoch_values) < 2:
        return False
    
    # Get the two most recent swings
    swing1_idx, swing1_price = swings[1]  # Older swing
    swing2_idx, swing2_price = swings[0]  # Newer swing
    
    stoch1 = stoch_values[1]  # Older stochastic value
    stoch2 = stoch_values[0]  # Newer stochastic value
    
    if divergence_type == 'bullish':
        # Price makes lower low, stochastic makes higher low
        price_lower_low = swing2_price < swing1_price
        stoch_higher_low = stoch2 > stoch1
        return price_lower_low and stoch_higher_low
        
    elif divergence_type == 'bearish':
        # Price makes higher high, stochastic makes lower high
        price_higher_high = swing2_price > swing1_price
        stoch_lower_high = stoch2 < stoch1
        return price_higher_high and stoch_lower_high
    
    return False