# Trading System Session Detection

This repository contains a trading session detection system that determines the active trading session based on timestamps from OHLC Parquet data files.

## Features

- **Real-time session detection** based on most recent timestamps in Parquet files
- **Four trading sessions**: Asia (03:00-07:00), London (09:00-12:00), NY_AM (14:00-18:00), NY_PM (21:00-23:00)
- **Continuous monitoring** every minute via main.py runner
- **Importable module** for use by other scripts
- **DataFrame output** for easy integration with other components

## Files

- `session_detection.py` - Core session detection logic
- `main.py` - Continuous runner script (executes every minute)
- `test_session_detection.py` - Comprehensive test suite
- `US100.cash.parquet` - Sample OHLC data file
- `US500.cash.parquet` - Sample OHLC data file

## Usage

### Running Session Detection Once

```bash
python3 session_detection.py
```

**Example Output:**
```
Trading Session Detection
========================================
Timestamp: 2025-07-14 11:59:00
Active Session: London

Session DataFrame:
          Timestamp Session
2025-07-14 11:59:00  London
```

### Running Continuous Monitoring

```bash
python3 main.py
```

**Example Output:**
```
Trading System - Session Monitor
==================================================
Starting continuous session detection (every 60 seconds)
Press Ctrl+C to stop

[2025-07-16 11:00:09] Timestamp: 2025-07-14 11:59:00 | Active Session: London
[2025-07-16 11:01:09] Timestamp: 2025-07-14 11:59:00 | Active Session: London
...
```

Press `Ctrl+C` to stop the continuous monitoring.

### Using as an Imported Module

```python
import session_detection as sd

# Get current session
timestamp, session = sd.get_current_session()
print(f"Current session: {session}")

# Create DataFrame for other scripts
df = sd.create_session_dataframe(timestamp, session)
print(df)
```

## Trading Sessions

| Session | Time Range | Description |
|---------|------------|-------------|
| Asia    | 03:00-07:00| Asian trading hours |
| London  | 09:00-12:00| London trading hours |
| NY_AM   | 14:00-18:00| New York morning session |
| NY_PM   | 21:00-23:00| New York evening session |
| Closed  | Other times| Markets closed |

## Testing

### Run the Test Suite

```bash
python3 test_session_detection.py
```

This tests:
- Session boundary detection (21 test cases)
- Parquet file reading functionality
- DataFrame creation

### Manual Testing Steps

1. **Test session detection logic**:
   ```bash
   python3 session_detection.py
   ```
   Verify the output shows correct session for the timestamp.

2. **Test continuous operation**:
   ```bash
   python3 main.py
   ```
   Let it run for a few minutes, then stop with Ctrl+C.

3. **Test import functionality**:
   ```bash
   python3 -c "import session_detection; print(session_detection.get_current_session())"
   ```

### Testing with Different Timestamps

To test with different Parquet file timestamps, you would:
1. Replace the existing Parquet files with data containing different timestamps
2. Run the session detection script
3. Verify the session matches the expected session for that time

## Requirements

- Python 3.6+
- pandas
- pyarrow

Install dependencies:
```bash
pip install pandas pyarrow
```

## Implementation Details

- Reads all `*.parquet` files in the current directory
- Combines Date and Timestamp columns to create full datetime
- Finds the most recent timestamp across all files
- Determines session based on hour of the timestamp
- Handles errors gracefully with informative messages
- Uses signal handlers for graceful shutdown in continuous mode