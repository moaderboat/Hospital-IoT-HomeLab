#!/usr/bin/env python3
"""
Secure System - Sensor Publisher
Reads DATAQ inline pressure sensor via ADS1115 ADC and publishes data via HTTP POST

This simulates a "network-connected IoT sensor" that publishes
pressure readings to the SECURE control system over HTTP.

✓ SECURE: Publishes to authenticated endpoint with validation

Pi #6 (Secure System) - 10.30.0.25 (VLAN30)
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import requests
import json
import hmac
import hashlib
from datetime import datetime

# Configuration
CONTROL_API_URL = "http://localhost:5000/sensor"  # Balloon control API
PUBLISH_INTERVAL = 0.5  # seconds (2 Hz - slower to let attack dominate during demo)
SENSOR_ID = "dataq-secure"

# HMAC signing (added 2026-11-10) - shares /etc/balloon-demo/hmac.conf with
# balloon_control_secure.py. Readings are signed only when MODE is monitor or
# enforce; with MODE=off (or no file) the publisher behaves exactly as before.
HMAC_CONFIG_PATH = "/etc/balloon-demo/hmac.conf"

def load_hmac_config(path=HMAC_CONFIG_PATH):
    """Read hmac.conf. Returns (mode, key_bytes)."""
    cfg = {"MODE": "off", "KEY": ""}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip().upper()] = v.strip()
    except Exception as e:
        print(f"HMAC config not loaded ({e}) - publishing unsigned")
    return cfg["MODE"].lower(), cfg["KEY"].encode()

HMAC_MODE, HMAC_KEY = load_hmac_config()
SIGNING_ENABLED = HMAC_MODE in ("monitor", "enforce") and bool(HMAC_KEY)

def signed_post(url, data, timeout):
    """POST data as JSON with X-Timestamp and X-Signature headers."""
    body = json.dumps(data, separators=(",", ":")).encode()
    ts = f"{time.time():.6f}"
    sig = hmac.new(HMAC_KEY, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Signature": sig,
    }
    return requests.post(url, data=body, headers=headers, timeout=timeout)

# DATAQ sensor constants
# A0 = 100 PSI upstream sensor (2000361-100H), A1 = 100 PSI downstream sensor (2000361-100H)
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
    print("=" * 60)
    print("SECURE SYSTEM - Sensor Publisher")
    print("=" * 60)
    print(f"Sensor ID: {SENSOR_ID}")
    print(f"Publishing to: {CONTROL_API_URL}")
    print(f"Interval: {PUBLISH_INTERVAL}s")
    print(f"HMAC signing: {'ON' if SIGNING_ENABLED else 'off'} (mode={HMAC_MODE}, key {'set' if HMAC_KEY else 'NOT set'})")
    print("=" * 60)

    # Initialize I2C and ADS1115 ADC
    # BSS138 level shifter sits between Pi (3.3V) and ADS1115 (5V) on SCL/SDA
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        chan_a1 = AnalogIn(ads, 1)  # A1 = 100 PSI downstream sensor (PRIMARY CONTROL)
        chan_a0 = AnalogIn(ads, 0)  # A0 = 100 PSI upstream sensor (upstream monitoring)
        print("ADS1115 ADC initialized (I2C via BSS138 level shifter)")
        print("DATAQ 100 PSI sensor on channel A1 (downstream, primary)")
        print("DATAQ 100 PSI sensor on channel A0 (upstream, monitoring)")
    except Exception as e:
        print(f"✗ Error initializing ADS1115/DATAQ sensor: {e}")
        return 1

    print("\nStarting sensor publication loop...")
    print("(Ctrl+C to stop)")
    print("-" * 60)

    publish_count = 0
    error_count = 0

    try:
        while True:
            try:
                # Read both sensors
                voltage_a1 = chan_a1.voltage
                voltage_a0 = chan_a0.voltage

                # Convert to PSI — use downstream A1 as primary control value
                pressure_psi = voltage_to_psi(voltage_a1, PRESSURE_MAX_A1)
                pressure_upstream_psi = voltage_to_psi(voltage_a0, PRESSURE_MAX_A0)

                # Prepare data payload — control API uses 'pressure' for control decisions
                data = {
                    "pressure": round(pressure_psi, 4),           # A1 downstream (primary)
                    "pressure_upstream": round(pressure_upstream_psi, 4),  # A0 upstream
                    "voltage_a1": round(voltage_a1, 3),
                    "voltage_a0": round(voltage_a0, 3),
                    "timestamp": datetime.now().isoformat(),
                    "source": SENSOR_ID,
                    "sensor_type": "dataq-100psi-ads1115-bss138"
                }

                # Publish to control API (signed when HMAC is enabled)
                if SIGNING_ENABLED:
                    response = signed_post(CONTROL_API_URL, data, timeout=2)
                else:
                    response = requests.post(
                        CONTROL_API_URL,
                        json=data,
                        timeout=2
                    )

                if response.status_code == 200:
                    publish_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Downstream: {pressure_psi:.1f} PSI | "
                          f"Upstream: {pressure_upstream_psi:.1f} PSI | "
                          f"OK: {publish_count} | Errors: {error_count}")
                else:
                    error_count += 1
                    print(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                error_count += 1
                print(f"Connection refused - is balloon_control_secure.py running?")
            except requests.exceptions.Timeout:
                error_count += 1
                print(f"Request timeout")
            except Exception as e:
                error_count += 1
                print(f"Error: {e}")

            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Sensor publisher stopped")
        print(f"  Total published: {publish_count}")
        print(f"  Total errors: {error_count}")
        print("=" * 60)
        return 0

if __name__ == "__main__":
    exit(main())
