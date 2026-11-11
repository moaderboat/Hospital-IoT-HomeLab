#!/usr/bin/env python3
"""
Sequent 8-RELAYS HAT Test Script
Tests relay control for air pump and solenoid valve

Hardware:
  - Sequent Microsystems 8-RELAYS HAT (I2C address 0x20)
  - Relay 1: Air Pump (12V DC, 10A)
  - Relay 2: Solenoid Valve (12V DC, normally closed)

Usage: python3 test_relays.py
"""

import time
import sys

try:
    import lib8relind
except ImportError:
    print("✗ Error: lib8relind not installed")
    print("\nInstall with:")
    print("  cd ~")
    print("  git clone https://github.com/SequentMicrosystems/8relind-rpi.git")
    print("  cd 8relind-rpi/python")
    print("  sudo python3 setup.py install")
    sys.exit(1)

# Relay assignments
RELAY_PUMP = 1   # Air pump
RELAY_VALVE = 2  # Solenoid valve

# Stack level (0 for first HAT)
STACK = 0

def test_relay(relay_num, name):
    """Test a single relay on/off"""
    print(f"\nTesting Relay {relay_num} ({name}):")
    print(f"  Turning ON...")
    lib8relind.set(STACK, relay_num, 1)
    time.sleep(2)

    print(f"  Turning OFF...")
    lib8relind.set(STACK, relay_num, 0)
    time.sleep(1)
    print(f"  ✓ Relay {relay_num} test complete")

def main():
    print("=" * 50)
    print("Sequent 8-RELAYS HAT Test")
    print("=" * 50)

    # Check if HAT is detected
    try:
        # Try to read relay status to verify HAT is present
        status = lib8relind.get_all(STACK)
        print(f"✓ 8-RELAYS HAT detected at stack {STACK}")
        print(f"  Current relay status: {bin(status)}")
    except Exception as e:
        print(f"✗ Error: Cannot communicate with 8-RELAYS HAT")
        print(f"  {e}")
        print("\nTroubleshooting:")
        print("  1. Check HAT is properly seated on GPIO pins")
        print("  2. Verify I2C is enabled: sudo raspi-config → Interface Options → I2C")
        print("  3. Check I2C device: i2cdetect -y 1 (should see 0x20)")
        print("  4. Verify lib8relind installed correctly")
        return 1

    # Turn off all relays first
    print("\nInitializing: Turning OFF all relays...")
    lib8relind.set_all(STACK, 0)
    time.sleep(1)
    print("  ✓ All relays OFF")

    # Test individual relays
    print("\n" + "=" * 50)
    print("Individual Relay Tests")
    print("=" * 50)

    test_relay(RELAY_PUMP, "Air Pump")
    test_relay(RELAY_VALVE, "Solenoid Valve")

    # Test inflation sequence
    print("\n" + "=" * 50)
    print("Inflation Sequence Test (3 seconds)")
    print("=" * 50)
    print("  1. Opening solenoid valve...")
    lib8relind.set(STACK, RELAY_VALVE, 1)
    time.sleep(0.5)

    print("  2. Starting air pump...")
    lib8relind.set(STACK, RELAY_PUMP, 1)

    print("  3. Inflating for 3 seconds...")
    time.sleep(3)

    print("  4. Stopping air pump...")
    lib8relind.set(STACK, RELAY_PUMP, 0)

    print("  5. Closing solenoid valve...")
    lib8relind.set(STACK, RELAY_VALVE, 0)

    print("  ✓ Inflation sequence complete")

    # Test deflation sequence
    print("\n" + "=" * 50)
    print("Deflation Sequence Test (2 seconds)")
    print("=" * 50)
    print("  1. Opening solenoid valve (pump OFF)...")
    lib8relind.set(STACK, RELAY_VALVE, 1)

    print("  2. Air escaping for 2 seconds...")
    time.sleep(2)

    print("  3. Closing solenoid valve...")
    lib8relind.set(STACK, RELAY_VALVE, 0)

    print("  ✓ Deflation sequence complete")

    # Final cleanup
    print("\nCleaning up: Turning OFF all relays...")
    lib8relind.set_all(STACK, 0)

    print("\n" + "=" * 50)
    print("Test Summary:")
    print("  ✓ 8-RELAYS HAT communication working")
    print("  ✓ Relay 1 (Air Pump) functioning")
    print("  ✓ Relay 2 (Solenoid Valve) functioning")
    print("  ✓ Inflation sequence tested")
    print("  ✓ Deflation sequence tested")
    print("\n⚠ WARNING: These were DRY TESTS with no pneumatic load")
    print("  Next: Connect actual air pump and solenoid valve")
    print("  Test with balloon attached and pressure monitoring")
    print("=" * 50)

    return 0

if __name__ == "__main__":
    exit(main())
