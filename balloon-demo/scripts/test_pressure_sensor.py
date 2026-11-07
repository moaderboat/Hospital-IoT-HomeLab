#!/usr/bin/env python3
"""
Test script for dual DATAQ 100 PSI pressure sensors via ADS1115 ADC

This script reads both DATAQ 2000361-100H pressure sensors through an
ADS1115 16-bit ADC and displays voltage and pressure readings.

Hardware Setup:
  - DATAQ 100 PSI upstream sensor on A0 (monitoring)
  - DATAQ 100 PSI downstream sensor on A1 (primary control)
  - ADS1115 connected via I²C (address 0x48)
  - BSS138 level shifter between Pi (3.3V) and ADC (5V)

Expected readings:
  - No pressure: ~0.5V = 0 PSI
  - Full scale: ~4.5V = 100 PSI
"""

import time
import sys

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except ImportError as e:
    print("ERROR: Required library not installed")
    print(f"  {e}")
    print("\nInstall with:")
    print("  sudo pip3 install adafruit-circuitpython-ads1x15")
    sys.exit(1)

# DATAQ 2000361-100H pressure sensor constants
VOLTAGE_MIN = 0.5   # V at 0 PSI (both sensors)
VOLTAGE_MAX = 4.5   # V at full scale (both sensors)
PRESSURE_MAX_A0 = 100.0  # PSI full scale — channel A0 (upstream)
PRESSURE_MAX_A1 = 100.0  # PSI full scale — channel A1 (downstream, primary control)

def voltage_to_psi(voltage, sensor_max_psi):
    """Convert DATAQ sensor voltage to PSI. sensor_max_psi = 100.0"""
    if voltage < VOLTAGE_MIN:
        return 0.0
    if voltage > VOLTAGE_MAX:
        return sensor_max_psi
    return (voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN) * sensor_max_psi

def main():
    print("=" * 70)
    print("DATAQ Dual 100 PSI Pressure Sensor Test")
    print("=" * 70)
    print("Sensors: DATAQ 2000361-100H (0-100 PSI)")
    print("ADC: ADS1115 16-bit (I²C address 0x48)")
    print("Channels: A0 (upstream), A1 (downstream/primary)")
    print("=" * 70)

    # Initialize I2C and ADS1115
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        chan_a0 = AnalogIn(ads, 0)  # A0 = 100 PSI upstream sensor (upstream monitoring)
        chan_a1 = AnalogIn(ads, 1)  # A1 = 100 PSI downstream sensor (PRIMARY CONTROL)
        print("✓ ADS1115 ADC initialized (I2C via BSS138 level shifter)")
        print("✓ DATAQ 100 PSI sensor on channel A0 (upstream, monitoring)")
        print("✓ DATAQ 100 PSI sensor on channel A1 (downstream, primary)")
    except Exception as e:
        print(f"✗ Error initializing ADS1115: {e}")
        print("\nTroubleshooting:")
        print("  1. Check I²C is enabled: sudo raspi-config → Interface Options → I2C")
        print("  2. Check wiring: SDA (Pin 3), SCL (Pin 5), VDD (5V), GND")
        print("  3. Check I²C devices: i2cdetect -y 1")
        print("     (Should show 0x48 for ADS1115)")
        return 1

    print("\nReading pressure sensors...")
    print("(Press Ctrl+C to exit)")
    print("-" * 70)
    print(f"{'Time':<12} {'A0 Voltage':<12} {'A0 PSI':<12} {'A1 Voltage':<12} {'A1 PSI':<12}")
    print("-" * 70)

    sample_count = 0

    try:
        while True:
            # Read both sensors
            voltage_a0 = chan_a0.voltage
            voltage_a1 = chan_a1.voltage

            # Convert to PSI — use downstream A1 as primary control value
            pressure_a0 = voltage_to_psi(voltage_a0, PRESSURE_MAX_A0)
            pressure_a1 = voltage_to_psi(voltage_a1, PRESSURE_MAX_A1)

            sample_count += 1

            # Display
            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp:<12} {voltage_a0:>6.3f}V      {pressure_a0:>6.2f} PSI   "
                  f"{voltage_a1:>6.3f}V      {pressure_a1:>6.2f} PSI")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("Test Complete")
        print("=" * 70)
        print(f"  Total samples: {sample_count}")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    exit(main())
