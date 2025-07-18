# Trading System - Divergence Detection

A real-time trading system for detecting specific divergence patterns using stochastic indicators and correlated pair analysis on OHLC market data.

## Features

This system detects the following divergence patterns:

### Stochastic Divergence
- **Bullish Divergence**: Price breaks below reference level and forms lower swing lows while stochastic indicator forms higher lows
- **Bearish Divergence**: Price breaks above reference level and forms higher swing highs while stochastic indicator forms lower highs

### Correlated Pair Divergence
- **Swing Failure (Bullish)**: Both pairs break below reference levels, one forms lower lows while the other forms higher lows
- **Swing Failure (Bearish)**: Both pairs break above reference levels, one forms higher highs while the other forms lower highs
- **Fake Breakout (Bullish)**: One pair breaks below reference level while correlated pair fails to break and forms higher low
- **Fake Breakout (Bearish)**: One pair breaks above reference level while correlated pair fails to break and forms lower high

## Components

### Core Classes

1. **SessionDetector** (`session_detector.py`)
   - Detects active trading sessions: London (0), NY_AM (1), NY_PM (2)
   - Based on UTC time ranges

2. **ReferenceLevelsCalculator** (`reference_levels_calculator.py`)
   - Calculates support and resistance levels using percentile-based analysis
   - Provides breakout detection functionality

3. **DivergenceDetector** (`divergence_detector.py`)
   - Main orchestrator for divergence pattern detection
   - Integrates all components and manages detection logic

### Utility Functions

4. **SwingDetector** (`swing_detector.py`)
   - Detects swing highs/lows using 3-consecutive-candle pattern
   - Calculates stochastic oscillator (3,3,3 settings)
   - Provides divergence analysis utilities

## Usage

### Basic Usage

```python
from divergence_detector import DivergenceDetector
import pandas as pd

# Load your OHLC data
symbols_data = {
    'US100.cash': pd.read_parquet('US100.cash.parquet'),
    'US500.cash': pd.read_parquet('US500.cash.parquet')
}

# Initialize detector
detector = DivergenceDetector()

# Scan for divergences
setups_df = detector.scan_for_divergences(symbols_data)

# Display results
print(f"Detected {len(setups_df)} setups")
print(setups_df)
```

### Running the Main System

```bash
python main.py
```

This runs the complete system in a loop, processing data and detecting divergence patterns.

## Output Format

The system outputs detected setups in a pandas DataFrame with columns:

- `Symbol`: Trading symbol (e.g., "US100.cash", "US500.cash")
- `Timestamp`: Time of detection (HH:MM format)
- `Session`: Trading session (0=London, 1=NY_AM, 2=NY_PM)
- `Direction`: Trade direction (0=Bullish/Long, 1=Bearish/Short)
- `Setup Type`: Pattern type (0=Stochastic Divergence, 1=Correlated Pair Swing Failure, 2=Correlated Pair Fake Breakout)

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- pandas >= 2.0.0
- numpy >= 1.24.0
- pyarrow >= 12.0.0
- scikit-learn >= 1.3.0

### Data Format

The system expects OHLC data in parquet format with columns:
- `Date`: Date in YYYY.MM.DD format
- `Timestamp`: Time in HH:MM format
- `Open`: Opening price
- `High`: High price
- `Low`: Low price
- `Close`: Closing price

## Testing

### Debug Scripts

1. **debug_system.py**: Tests individual components
2. **detailed_debug.py**: Detailed analysis of detection process
3. **test_divergence.py**: Tests with both real and synthetic data
4. **final_test.py**: Comprehensive system testing

### Running Tests

```bash
# Test individual components
python debug_system.py

# Test divergence detection with detailed output
python detailed_debug.py

# Test with synthetic data (should detect patterns)
python test_divergence.py

# Comprehensive testing with different data sizes
python final_test.py
```

## Configuration

### Key Parameters

- **Swing Detection**: 3-candle pattern (configurable in `swing_detector.py`)
- **Stochastic Settings**: (3,3,3) - K period, D period, smoothing
- **Analysis Window**: Last 1000 records for performance
- **Lookback Period**: 40 candles for swing analysis
- **Reference Levels**: Based on percentile analysis (5th, 10th, 90th, 95th)

### Session Times (UTC)

- **London**: 08:00 - 13:00
- **NY_AM**: 13:00 - 17:00 (overlaps with London)
- **NY_PM**: 17:00 - 22:00

## Performance Optimization

The system is optimized for real-time processing:

- Processes only recent data (last 1000 records) to maintain performance
- Uses efficient pandas operations
- Implements duplicate prevention
- Rounds all float values to 2 decimal places

## Integration

The system is designed for integration with gradient boosting models:

1. Detected setups are saved in a standardized DataFrame format
2. Duplicate prevention ensures clean training data
3. Multiple setup types provide diverse pattern recognition
4. Session-based categorization allows time-aware modeling

## Limitations

- Divergence patterns are relatively rare in market data
- The system requires sufficient historical data for swing detection
- Reference levels are recalculated on each run (could be cached for production)
- Currently supports only two correlated pairs (US100.cash and US500.cash)

## Future Enhancements

- Add more correlated pair combinations
- Implement backtesting capabilities
- Add real-time data feed integration
- Include additional technical indicators
- Implement machine learning model integration
- Add configuration file support