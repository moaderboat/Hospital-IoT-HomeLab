#!/usr/bin/env python3
"""
Test script for DATAQ inline pressure sensor via ADS1115 ADC

This script reads the DATAQ 2000361-30H pressure sensor through an
ADS1115 16-bit ADC and displays voltage and pressure readings.

Hardware Setup:
  - DATAQ sensor connected to ADS1115 channel A0
  - ADS1115 connected via I²C (address 0x48)
  - BSS138 level shifter between Pi (3.3V) and ADC (5V)

Expected readings:
  - No pressure: ~0.5V = 0 PSI
  - Full scale: ~4.5V = 30 PSI
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

# DATAQ 2000361-30H pressure sensor constants
VOLTAGE_MIN = 0.5  # 0 PSI
VOLTAGE_MAX = 4.5  # 30 PSI
PRESSURE_MAX = 30.0  # PSI

def voltage_to_psi(voltage):
    """Convert DATAQ sensor voltage to PSI"""
    if voltage < VOLTAGE_MIN:
        return 0.0  # Below minimum = no pressure
    if voltage > VOLTAGE_MAX:
        return PRESSURE_MAX  # Above maximum = saturated

    # Linear conversion: PSI = (V - 0.5) / 4.0 * 30.0
    psi = (voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN) * PRESSURE_MAX
    return psi

def main():
    print("=" * 60)
    print("DATAQ Inline Pressure Sensor Test")
    print("=" * 60)
    print("Sensor: DATAQ 2000361-30H (0-30 PSI)")
    print("ADC: ADS1115 16-bit (I²C address 0x48)")
    print("Channel: A0")
    print("=" * 60)

    # Initialize I2C and ADS1115
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, 0)  # Pressure sensor on channel A0
        print("✓ ADS1115 ADC initialized")
        print("✓ DATAQ pressure sensor on channel A0")
    except Exception as e:
        print(f"✗ Error initializing ADS1115: {e}")
        print("\nTroubleshooting:")
        print("  1. Check I²C is enabled: sudo raspi-config → Interface Options → I2C")
        print("  2. Check wiring: SDA (Pin 3), SCL (Pin 5), VDD (5V), GND")
        print("  3. Check I²C devices: i2cdetect -y 1")
        print("     (Should show 0x48 for ADS1115)")
        return 1

    print("\nReading pressure sensor...")
    print("(Press Ctrl+C to exit)")
    print("-" * 60)
    print(f"{'Time':<12} {'Voltage':<12} {'Pressure':<12} {'Status':<20}")
    print("-" * 60)

    sample_count = 0
    min_voltage = float('inf')
    max_voltage = float('-inf')
    min_pressure = float('inf')
    max_pressure = float('-inf')

    try:
        while True:
            # Read voltage from ADC
            voltage = chan.voltage

            # Convert to PSI
            pressure = voltage_to_psi(voltage)

            # Track min/max
            sample_count += 1
            min_voltage = min(min_voltage, voltage)
            max_voltage = max(max_voltage, voltage)
            min_pressure = min(min_pressure, pressure)
            max_pressure = max(max_pressure, pressure)

            # Status indicators
            status = ""
            if voltage < 0.4:
                status = "⚠ LOW VOLTAGE"
            elif voltage < VOLTAGE_MIN:
                status = "No pressure"
            elif voltage > VOLTAGE_MAX:
                status = "⚠ SATURATED"
            elif voltage > 4.6:
                status = "⚠ HIGH VOLTAGE"
            elif pressure > 5.0:
                status = "⚠ HIGH PRESSURE"
            else:
                status = "Normal"

            # Display
            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp:<12} {voltage:>6.3f}V      {pressure:>6.2f} PSI   {status:<20}")

            # Show statistics every 10 samples
            if sample_count % 10 == 0:
                print(f"  [Stats] Samples: {sample_count}, "
                      f"V: {min_voltage:.3f}-{max_voltage:.3f}, "
                      f"PSI: {min_pressure:.2f}-{max_pressure:.2f}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Test Complete")
        print("=" * 60)
        print(f"  Total samples: {sample_count}")
        print(f"  Voltage range: {min_voltage:.3f}V - {max_voltage:.3f}V")
        print(f"  Pressure range: {min_pressure:.2f} - {max_pressure:.2f} PSI")
        print("=" * 60)

        # Sensor health check
        print("\nSensor Health Check:")
        if min_voltage < 0.4:
            print("  ⚠ WARNING: Voltage too low - check sensor power (12V excitation)")
        elif min_voltage > 0.6 and max_pressure < 0.1:
            print("  ⚠ WARNING: Offset voltage high - check sensor zero calibration")
        elif max_voltage > 4.6:
            print("  ⚠ WARNING: Voltage too high - check for overpressure or wiring")
        else:
            print("  ✓ Sensor readings appear normal")

        print("=" * 60)
        return 0

if __name__ == "__main__":
    exit(main())
