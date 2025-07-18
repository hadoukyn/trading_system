"""
ReferenceLevelsCalculator class for calculating reference levels for each symbol.
"""
import pandas as pd
import numpy as np


class ReferenceLevelsCalculator:
    def __init__(self):
        self.reference_levels_df = pd.DataFrame()
        
    def calculate_support_resistance(self, data_df, symbol, lookback_periods=100):
        """
        Calculate support and resistance levels based on swing highs and lows.
        
        Args:
            data_df (pd.DataFrame): OHLC data
            symbol (str): Symbol name (e.g., 'US100.cash')
            lookback_periods (int): Number of periods to look back for levels
            
        Returns:
            dict: Dictionary with support and resistance levels
        """
        if len(data_df) < lookback_periods:
            lookback_periods = len(data_df)
            
        # Get recent data
        recent_data = data_df.tail(lookback_periods).copy()
        
        # Calculate basic levels using high/low percentiles
        resistance_levels = [
            round(recent_data['High'].quantile(0.95), 2),  # 95th percentile high
            round(recent_data['High'].quantile(0.90), 2),  # 90th percentile high
            round(recent_data['High'].max(), 2)             # Absolute high
        ]
        
        support_levels = [
            round(recent_data['Low'].quantile(0.05), 2),   # 5th percentile low
            round(recent_data['Low'].quantile(0.10), 2),   # 10th percentile low
            round(recent_data['Low'].min(), 2)              # Absolute low
        ]
        
        # Calculate pivot levels
        pivot = round((recent_data['High'].iloc[-1] + recent_data['Low'].iloc[-1] + recent_data['Close'].iloc[-1]) / 3, 2)
        
        return {
            'Symbol': symbol,
            'Resistance_1': resistance_levels[1],
            'Resistance_2': resistance_levels[0], 
            'Resistance_3': resistance_levels[2],
            'Support_1': support_levels[1],
            'Support_2': support_levels[0],
            'Support_3': support_levels[2],
            'Pivot': pivot
        }
    
    def calculate_reference_levels(self, symbols_data):
        """
        Calculate reference levels for all symbols.
        
        Args:
            symbols_data (dict): Dictionary with symbol names as keys and DataFrames as values
        """
        levels_data = []
        
        for symbol, data_df in symbols_data.items():
            levels = self.calculate_support_resistance(data_df, symbol)
            levels_data.append(levels)
        
        # Store in reference_levels_df
        self.reference_levels_df = pd.DataFrame(levels_data)
        
        return self.reference_levels_df
    
    def get_reference_level_for_breakout(self, symbol, price, direction):
        """
        Get the appropriate reference level for breakout detection.
        
        Args:
            symbol (str): Symbol name
            price (float): Current price
            direction (str): 'above' for bearish, 'below' for bullish
            
        Returns:
            float: Reference level price or None if not found
        """
        if self.reference_levels_df.empty:
            return None
            
        symbol_levels = self.reference_levels_df[self.reference_levels_df['Symbol'] == symbol]
        if symbol_levels.empty:
            return None
            
        symbol_levels = symbol_levels.iloc[0]
        
        if direction == 'below':
            # For bullish setups, check if price broke below support levels
            support_levels = [
                symbol_levels['Support_1'],
                symbol_levels['Support_2'], 
                symbol_levels['Support_3']
            ]
            # Return the highest support level that was broken
            broken_supports = [level for level in support_levels if price < level]
            return max(broken_supports) if broken_supports else None
            
        elif direction == 'above':
            # For bearish setups, check if price broke above resistance levels
            resistance_levels = [
                symbol_levels['Resistance_1'],
                symbol_levels['Resistance_2'],
                symbol_levels['Resistance_3']
            ]
            # Return the lowest resistance level that was broken
            broken_resistances = [level for level in resistance_levels if price > level]
            return min(broken_resistances) if broken_resistances else None
            
        return None