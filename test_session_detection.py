"""
Test script for session detection functionality.

This script tests various edge cases and validates the session detection logic.
"""

import session_detection as sd
from datetime import datetime


def test_session_boundaries():
    """Test session detection at various time boundaries."""
    print("Testing Session Boundaries")
    print("=" * 40)
    
    test_cases = [
        # (hour, minute, expected_session)
        (2, 59, "Closed"),     # Just before Asia
        (3, 0, "Asia"),        # Asia start
        (5, 30, "Asia"),       # Asia middle
        (6, 59, "Asia"),       # Asia end
        (7, 0, "Closed"),      # Just after Asia
        (8, 59, "Closed"),     # Just before London
        (9, 0, "London"),      # London start
        (10, 30, "London"),    # London middle
        (11, 59, "London"),    # London end
        (12, 0, "Closed"),     # Just after London
        (13, 59, "Closed"),    # Just before NY_AM
        (14, 0, "NY_AM"),      # NY_AM start
        (16, 30, "NY_AM"),     # NY_AM middle
        (17, 59, "NY_AM"),     # NY_AM end
        (18, 0, "Closed"),     # Just after NY_AM
        (20, 59, "Closed"),    # Just before NY_PM
        (21, 0, "NY_PM"),      # NY_PM start
        (22, 30, "NY_PM"),     # NY_PM middle
        (22, 59, "NY_PM"),     # NY_PM end
        (23, 0, "Closed"),     # Just after NY_PM
        (0, 30, "Closed"),     # Midnight
    ]
    
    passed = 0
    failed = 0
    
    for hour, minute, expected in test_cases:
        test_time = datetime(2025, 7, 16, hour, minute)
        actual = sd.determine_session(test_time)
        
        status = "✓" if actual == expected else "✗"
        print(f"{status} {test_time.strftime('%H:%M')} -> {actual:8} (expected: {expected})")
        
        if actual == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def test_parquet_file_reading():
    """Test reading from actual Parquet files."""
    print("\nTesting Parquet File Reading")
    print("=" * 40)
    
    try:
        timestamp = sd.get_most_recent_timestamp()
        if timestamp is None:
            print("✗ Failed to read timestamp from Parquet files")
            return False
        
        print(f"✓ Successfully read timestamp: {timestamp}")
        
        session = sd.determine_session(timestamp)
        print(f"✓ Session determined: {session}")
        
        df = sd.create_session_dataframe(timestamp, session)
        print(f"✓ DataFrame created with shape: {df.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading Parquet files: {e}")
        return False


def main():
    """Run all tests."""
    print("Session Detection Test Suite")
    print("=" * 50)
    
    test1_pass = test_session_boundaries()
    test2_pass = test_parquet_file_reading()
    
    print(f"\nOverall Test Results:")
    print(f"Session Boundaries: {'PASS' if test1_pass else 'FAIL'}")
    print(f"Parquet Reading: {'PASS' if test2_pass else 'FAIL'}")
    
    if test1_pass and test2_pass:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())