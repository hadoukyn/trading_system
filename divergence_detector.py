"""
DivergenceDetector class for detecting various divergence patterns.
"""
import pandas as pd
import numpy as np
from session_detector import SessionDetector
from reference_levels_calculator import ReferenceLevelsCalculator
from swing_detector import (
    detect_swing_highs_lows, 
    calculate_stochastic, 
    find_recent_swings, 
    detect_divergence
)


class DivergenceDetector:
    def __init__(self):
        self.session_detector = SessionDetector()
        self.reference_levels_calculator = ReferenceLevelsCalculator()
        self.detected_setups_df = pd.DataFrame(columns=[
            'Symbol', 'Timestamp', 'Session', 'Direction', 'Setup Type'
        ])
        self.correlated_pairs = {
            'US100.cash': 'US500.cash',
            'US500.cash': 'US100.cash'
        }
    
    def prepare_data(self, symbols_data, max_records=1000):
        """
        Prepare data by adding swing detection and stochastic indicators.
        Use only recent data for efficiency.
        
        Args:
            symbols_data (dict): Dictionary with symbol DataFrames
            max_records (int): Maximum number of recent records to process
            
        Returns:
            dict: Enhanced DataFrames with technical indicators
        """
        enhanced_data = {}
        
        for symbol, data_df in symbols_data.items():
            # Use only recent data for efficiency
            recent_data = data_df.tail(max_records).copy()
            print(f"Processing {symbol}: {len(recent_data)} recent records")
            
            # Add swing detection
            df_with_swings = detect_swing_highs_lows(recent_data)
            
            # Add stochastic indicator (3,3,3 settings)
            df_enhanced = calculate_stochastic(df_with_swings, k_period=3, d_period=3, smooth_k=3)
            
            enhanced_data[symbol] = df_enhanced
            
        return enhanced_data
    
    def detect_stochastic_divergence(self, symbol, data_df, session_df, reference_levels):
        """
        Detect stochastic divergence patterns.
        
        Args:
            symbol (str): Symbol name
            data_df (pd.DataFrame): Enhanced OHLC data
            session_df (pd.DataFrame): Session data
            reference_levels (pd.DataFrame): Reference levels
            
        Returns:
            list: List of detected setups
        """
        setups = []
        
        # Work with the last 100 candles for analysis (increased from 50)
        analysis_window = min(100, len(data_df))
        recent_data = data_df.tail(analysis_window).copy().reset_index(drop=True)
        recent_sessions = session_df.tail(analysis_window).copy().reset_index(drop=True)
        
        # Analyze only the last few candles for potential setups
        start_idx = max(20, analysis_window - 30)  # Check last 30 candles only
        
        for i in range(start_idx, len(recent_data)):
            current_candle = recent_data.iloc[i]
            current_session = recent_sessions.iloc[i]['Session'] if i < len(recent_sessions) else 0
            
            # Check for bullish divergence (break below reference level)
            reference_level = self.reference_levels_calculator.get_reference_level_for_breakout(
                symbol, current_candle['Low'], 'below'
            )
            
            if reference_level is not None:
                # Find recent swing lows (increased lookback)
                swing_lows = find_recent_swings(recent_data, i, 'low', max_lookback=40)
                
                if len(swing_lows) >= 2:
                    # Get stochastic values for the swing lows
                    stoch_values = [recent_data.iloc[idx]['Stoch_K'] for idx, _ in swing_lows]
                    
                    # Check for bullish divergence
                    if detect_divergence(swing_lows, stoch_values, 'bullish'):
                        setup = {
                            'Symbol': symbol,
                            'Timestamp': current_candle['Timestamp'],
                            'Session': int(current_session),
                            'Direction': 0,  # Bullish
                            'Setup Type': 0  # Stochastic Divergence
                        }
                        setups.append(setup)
                        print(f"DEBUG: Bullish stochastic divergence detected for {symbol} at {current_candle['Timestamp']}")
            
            # Check for bearish divergence (break above reference level)
            reference_level = self.reference_levels_calculator.get_reference_level_for_breakout(
                symbol, current_candle['High'], 'above'
            )
            
            if reference_level is not None:
                # Find recent swing highs (increased lookback)
                swing_highs = find_recent_swings(recent_data, i, 'high', max_lookback=40)
                
                if len(swing_highs) >= 2:
                    # Get stochastic values for the swing highs
                    stoch_values = [recent_data.iloc[idx]['Stoch_K'] for idx, _ in swing_highs]
                    
                    # Check for bearish divergence
                    if detect_divergence(swing_highs, stoch_values, 'bearish'):
                        setup = {
                            'Symbol': symbol,
                            'Timestamp': current_candle['Timestamp'],
                            'Session': int(current_session),
                            'Direction': 1,  # Bearish
                            'Setup Type': 0  # Stochastic Divergence
                        }
                        setups.append(setup)
                        print(f"DEBUG: Bearish stochastic divergence detected for {symbol} at {current_candle['Timestamp']}")
        
        return setups
    
    def detect_correlated_pair_divergence(self, symbols_data, session_df, reference_levels):
        """
        Detect correlated pair divergence patterns.
        
        Args:
            symbols_data (dict): Enhanced symbol DataFrames
            session_df (pd.DataFrame): Session data
            reference_levels (pd.DataFrame): Reference levels
            
        Returns:
            list: List of detected setups
        """
        setups = []
        
        # Check each correlated pair
        for symbol1, symbol2 in self.correlated_pairs.items():
            if symbol1 not in symbols_data or symbol2 not in symbols_data:
                continue
                
            data1 = symbols_data[symbol1]
            data2 = symbols_data[symbol2]
            
            # Analyze recent data - use smaller window for efficiency
            analysis_window = min(50, len(data1), len(data2))
            recent_data1 = data1.tail(analysis_window).copy().reset_index(drop=True)
            recent_data2 = data2.tail(analysis_window).copy().reset_index(drop=True)
            recent_sessions = session_df.tail(analysis_window).copy().reset_index(drop=True)
            
            # Check only the last few candles
            start_idx = max(10, analysis_window - 20)
            
            for i in range(start_idx, min(len(recent_data1), len(recent_data2))):
                candle1 = recent_data1.iloc[i]
                candle2 = recent_data2.iloc[i]
                current_session = recent_sessions.iloc[i]['Session'] if i < len(recent_sessions) else 0
                
                # Check for bullish correlated pair setups
                ref_level1 = self.reference_levels_calculator.get_reference_level_for_breakout(
                    symbol1, candle1['Low'], 'below'
                )
                ref_level2 = self.reference_levels_calculator.get_reference_level_for_breakout(
                    symbol2, candle2['Low'], 'below'
                )
                
                # Swing Failure Pattern
                if ref_level1 is not None and ref_level2 is not None:
                    swings1 = find_recent_swings(recent_data1, i, 'low', max_lookback=15)
                    swings2 = find_recent_swings(recent_data2, i, 'low', max_lookback=15)
                    
                    if len(swings1) >= 2 and len(swings2) >= 2:
                        # Check if one forms lower low and other forms higher low
                        swing1_lower = swings1[0][1] < swings1[1][1]  # Lower low
                        swing2_higher = swings2[0][1] > swings2[1][1]  # Higher low
                        
                        if swing1_lower and swing2_higher:
                            setup = {
                                'Symbol': symbol1,
                                'Timestamp': candle1['Timestamp'],
                                'Session': int(current_session),
                                'Direction': 0,  # Bullish
                                'Setup Type': 1  # Correlated Pair Swing Failure
                            }
                            setups.append(setup)
                
                # Fake Breakout Pattern
                if ref_level1 is not None and ref_level2 is None:
                    swings1 = find_recent_swings(recent_data1, i, 'low', max_lookback=15)
                    swings2 = find_recent_swings(recent_data2, i, 'low', max_lookback=15)
                    
                    if len(swings1) >= 1 and len(swings2) >= 1:
                        # Symbol1 broke below, symbol2 didn't and formed higher low
                        if swings2[0][1] > swings2[1][1] if len(swings2) >= 2 else True:
                            setup = {
                                'Symbol': symbol1,
                                'Timestamp': candle1['Timestamp'],
                                'Session': int(current_session),
                                'Direction': 0,  # Bullish
                                'Setup Type': 2  # Correlated Pair Fake Breakout
                            }
                            setups.append(setup)
                
                # Check for bearish correlated pair setups (similar logic but for highs)
                ref_level1_high = self.reference_levels_calculator.get_reference_level_for_breakout(
                    symbol1, candle1['High'], 'above'
                )
                ref_level2_high = self.reference_levels_calculator.get_reference_level_for_breakout(
                    symbol2, candle2['High'], 'above'
                )
                
                # Bearish Swing Failure Pattern
                if ref_level1_high is not None and ref_level2_high is not None:
                    swings1_high = find_recent_swings(recent_data1, i, 'high', max_lookback=15)
                    swings2_high = find_recent_swings(recent_data2, i, 'high', max_lookback=15)
                    
                    if len(swings1_high) >= 2 and len(swings2_high) >= 2:
                        # Check if one forms higher high and other forms lower high
                        swing1_higher = swings1_high[0][1] > swings1_high[1][1]  # Higher high
                        swing2_lower = swings2_high[0][1] < swings2_high[1][1]  # Lower high
                        
                        if swing1_higher and swing2_lower:
                            setup = {
                                'Symbol': symbol1,
                                'Timestamp': candle1['Timestamp'],
                                'Session': int(current_session),
                                'Direction': 1,  # Bearish
                                'Setup Type': 1  # Correlated Pair Swing Failure
                            }
                            setups.append(setup)
                
                # Bearish Fake Breakout Pattern
                if ref_level1_high is not None and ref_level2_high is None:
                    swings1_high = find_recent_swings(recent_data1, i, 'high', max_lookback=15)
                    swings2_high = find_recent_swings(recent_data2, i, 'high', max_lookback=15)
                    
                    if len(swings1_high) >= 1 and len(swings2_high) >= 1:
                        # Symbol1 broke above, symbol2 didn't and formed lower high
                        if swings2_high[0][1] < swings2_high[1][1] if len(swings2_high) >= 2 else True:
                            setup = {
                                'Symbol': symbol1,
                                'Timestamp': candle1['Timestamp'],
                                'Session': int(current_session),
                                'Direction': 1,  # Bearish
                                'Setup Type': 2  # Correlated Pair Fake Breakout
                            }
                            setups.append(setup)
        
        return setups
    
    def scan_for_divergences(self, symbols_data):
        """
        Main method to scan for all divergence patterns.
        
        Args:
            symbols_data (dict): Dictionary with symbol DataFrames
            
        Returns:
            pd.DataFrame: Updated detected_setups_df
        """
        # Prepare data with technical indicators
        enhanced_data = self.prepare_data(symbols_data)
        
        # Update session detection (use recent data only)
        first_symbol = list(symbols_data.keys())[0]
        recent_data_for_sessions = symbols_data[first_symbol].tail(1000)  # Last 1000 records
        session_df = self.session_detector.update_active_sessions(recent_data_for_sessions)
        
        # Calculate reference levels
        reference_levels = self.reference_levels_calculator.calculate_reference_levels(enhanced_data)
        
        all_setups = []
        
        # Detect stochastic divergences for each symbol
        for symbol in enhanced_data.keys():
            stoch_setups = self.detect_stochastic_divergence(
                symbol, enhanced_data[symbol], session_df, reference_levels
            )
            all_setups.extend(stoch_setups)
        
        # Detect correlated pair divergences
        corr_setups = self.detect_correlated_pair_divergence(
            enhanced_data, session_df, reference_levels
        )
        all_setups.extend(corr_setups)
        
        # Convert to DataFrame and remove duplicates
        if all_setups:
            new_setups_df = pd.DataFrame(all_setups)
            
            # Remove duplicates based on Symbol, Timestamp, Direction, Setup Type
            new_setups_df = new_setups_df.drop_duplicates(
                subset=['Symbol', 'Timestamp', 'Direction', 'Setup Type'],
                keep='last'
            )
            
            # Replace previous setups with new ones to avoid duplicates
            self.detected_setups_df = new_setups_df
        
        return self.detected_setups_df