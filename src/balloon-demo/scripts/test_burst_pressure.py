#!/usr/bin/env python3
"""
Burst Pressure Characterization Test
Incrementally pressurizes the 1L plastic bottle in 1 PSI steps to
determine burst pressure for setting safety thresholds.

Hardware:
  - DATAQ 100 PSI downstream sensor on ADS1115 channel A1 (primary control)
  - DATAQ 100 PSI upstream sensor on ADS1115 channel A0 (redundant monitoring)
  - ADS1115 via BSS138 level shifter (Pi 3.3V <-> ADC 5V)
  - Sequent 8-RELAYS HAT, STACK=0 (I2C 0x27)
  - Sequent 40A 3-relay HAT, STACK=0 (I2C 0x60)
    40A HAT Relay 3 = Pump (23A load)
    8-relay HAT Relay 2 = Solenoid INFLATE - Main line control (NC, opens on energize)
    8-relay HAT Relay 3 = Solenoid DOWNSTREAM - Closest to bottle (NC, opens on energize)
    8-relay HAT Relay 4 = Solenoid UPSTREAM - Closer to pump (NC, opens on energize)

  Physical flow: Pump → UPSTREAM (R4) → INFLATE (R2) → DOWNSTREAM (R3) → Bottle

Usage:
  python3 test_burst_pressure.py [--start PSI] [--step PSI] [--ceiling PSI] [--hold SEC]

Default: --start 5 --step 1 --ceiling 70 --hold 7

WARNING: This script is for burst characterization only.
         Use a blast shield / safety enclosure.
         Keep personnel clear of the bottle during test.
         Operator must monitor at all times and be ready on Ctrl+C.
"""

import time
import sys
import signal
import argparse
from datetime import datetime

# ── Hardware imports ──────────────────────────────────────────────────────────
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    SENSOR_AVAILABLE = True
except ImportError:
    print("⚠  ADS1115 library not available — sensor disabled")
    SENSOR_AVAILABLE = False

try:
    import lib8relind
    RELAY8_AVAILABLE = True
except ImportError:
    print("⚠  lib8relind not installed — 8-relay HAT control disabled")
    RELAY8_AVAILABLE = False

try:
    import lib3relind
    RELAY40A_AVAILABLE = True
except ImportError:
    print("⚠  lib3relind not installed — 40A relay HAT control disabled")
    RELAY40A_AVAILABLE = False

RELAYS_AVAILABLE = RELAY8_AVAILABLE and RELAY40A_AVAILABLE

# ── Configuration ─────────────────────────────────────────────────────────────
STACK_8RELAY = 0    # 8-RELAYS HAT stack level (I2C 0x27)
STACK_40A = 0       # 40A relay HAT stack level (I2C 0x60)

# Relay assignments (Physical flow: Pump → UPSTREAM → INFLATE → DOWNSTREAM → Bottle)
RELAY_PUMP       = 3   # Air pump (23A) - on 40A HAT relay 3
RELAY_INFLATE    = 2   # Main line control solenoid - on 8-relay HAT
RELAY_DOWNSTREAM = 3   # Closest to bottle (vent/deflate) - on 8-relay HAT
RELAY_UPSTREAM   = 4   # Closer to pump (high-pressure relief) - on 8-relay HAT

# DATAQ sensor voltage range (same for both sensors)
VOLTAGE_MIN = 0.5   # V at 0 PSI
VOLTAGE_MAX = 4.5   # V at full scale

PRESSURE_MAX_A1 = 100.0  # PSI — channel A1 (downstream primary) - 100 PSI DATAQ sensor
PRESSURE_MAX_A0 = 100.0  # PSI — channel A0 (upstream relief) - 100 PSI DATAQ sensor

# Test parameters (override with CLI args)
START_PRESSURE  = 5.0   # PSI — starting step (skip low pressure range)
STEP_SIZE       = 1.0   # PSI — increment per step
MAX_PRESSURE    = 70.0  # PSI — hard abort ceiling (do NOT exceed)
HOLD_SECONDS    = 7     # seconds to hold at each step before advancing
POLL_INTERVAL   = 0.5   # seconds between sensor readings during hold
PUMP_PULSE_DURATION = 0.1  # seconds per pump pulse (short bursts)

# Burst detection: if downstream drops this much in one poll cycle → burst
BURST_DROP_THRESHOLD = 1.5  # PSI

# Upstream relief auto-trigger
RELIEF_UPSTREAM_THRESHOLD = 60.0  # PSI — open relief if 100PSI sensor > this

# ── State ─────────────────────────────────────────────────────────────────────
pump_running      = False
inflate_open      = False
downstream_open   = False
upstream_open     = False
emergency_active  = False

# Results log
results = []   # list of dicts: {target_psi, actual_psi_15, actual_psi_30, held_s, event}

# ── Helpers ───────────────────────────────────────────────────────────────────

def voltage_to_psi(voltage, sensor_max_psi):
    """Linear conversion: DATAQ analog output → PSI"""
    if voltage < VOLTAGE_MIN:
        return 0.0
    if voltage > VOLTAGE_MAX:
        return sensor_max_psi
    return (voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN) * sensor_max_psi


# ── Direct hardware control functions ─────────────────────────────────────
def pump_on():
    """Turn pump ON (40A HAT relay 3)"""
    global pump_running
    if RELAY40A_AVAILABLE:
        lib3relind.set(STACK_40A, RELAY_PUMP, 1)
        pump_running = True

def pump_off():
    """Turn pump OFF (40A HAT relay 3)"""
    global pump_running
    if RELAY40A_AVAILABLE:
        lib3relind.set(STACK_40A, RELAY_PUMP, 0)
        pump_running = False

def open_inflate():
    """Open inflate solenoid (8-relay HAT relay 2)"""
    global inflate_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_INFLATE, 1)
        inflate_open = True

def close_inflate():
    """Close inflate solenoid (8-relay HAT relay 2)"""
    global inflate_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_INFLATE, 0)
        inflate_open = False

def open_downstream():
    """Open downstream solenoid (8-relay HAT relay 3) - closest to bottle"""
    global downstream_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_DOWNSTREAM, 1)
        downstream_open = True

def close_downstream():
    """Close downstream solenoid (8-relay HAT relay 3) - closest to bottle"""
    global downstream_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_DOWNSTREAM, 0)
        downstream_open = False

def open_upstream():
    """Open upstream solenoid (8-relay HAT relay 4) - closer to pump"""
    global upstream_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_UPSTREAM, 1)
        upstream_open = True

def close_upstream():
    """Close upstream solenoid (8-relay HAT relay 4) - closer to pump"""
    global upstream_open
    if RELAY8_AVAILABLE:
        lib8relind.set(STACK_8RELAY, RELAY_UPSTREAM, 0)
        upstream_open = False

def kill_all():
    """Emergency - turn everything OFF"""
    global pump_running, inflate_open, downstream_open, upstream_open
    if RELAY40A_AVAILABLE:
        lib3relind.set_all(STACK_40A, 0)
    if RELAY8_AVAILABLE:
        lib8relind.set_all(STACK_8RELAY, 0)
    pump_running = False
    inflate_open = False
    downstream_open = False
    upstream_open = False


def emergency_vent():
    """Immediately stop pump and open downstream + upstream. Call on Ctrl+C or burst."""
    global emergency_active
    emergency_active = True
    print("\n" + "!" * 60)
    print("EMERGENCY VENT — stopping pump, opening downstream + upstream")
    print("!" * 60)

    pump_off()
    close_inflate()
    time.sleep(0.1)
    open_upstream()
    open_downstream()
    print("  ✓ Pump OFF, vents OPEN")


# (Removed start_inflation and stop_inflation - use direct functions instead)


def read_pressures(chan_a1, chan_a0):
    """Return (psi_a1, psi_a0) - both are 100 PSI sensors."""
    if not SENSOR_AVAILABLE:
        return 0.0, 0.0
    try:
        psi_a1 = voltage_to_psi(chan_a1.voltage, PRESSURE_MAX_A1)
        psi_a0 = voltage_to_psi(chan_a0.voltage, PRESSURE_MAX_A0)
        return psi_a1, psi_a0
    except Exception as e:
        print(f"  ✗ Sensor read error: {e}")
        return None, None


def print_reading(target, psi_a1, psi_a0, elapsed, hold_s, event=""):
    ts = datetime.now().strftime("%H:%M:%S")
    bar_width = 30
    ratio = min(psi_a1 / MAX_PRESSURE, 1.0) if psi_a1 else 0
    bar = "#" * int(bar_width * ratio) + "-" * (bar_width - int(bar_width * ratio))
    tag = f"  ← {event}" if event else ""
    print(f"[{ts}] target={target:.1f}  A1={psi_a1:6.3f} PSI  A0={psi_a0:6.3f} PSI  "
          f"hold={elapsed:4.0f}/{hold_s}s  [{bar}]{tag}")


def print_results(results, burst_psi):
    print("\n" + "=" * 60)
    print("BURST PRESSURE TEST RESULTS")
    print("=" * 60)
    print(f"{'Target':>8}  {'A1(ctrl)':>12}  {'A0(backup)':>12}  {'Hold(s)':>8}  Event")
    print("-" * 60)
    for r in results:
        print(f"{r['target_psi']:>8.1f}  {r['actual_psi_15']:>12.3f}  "
              f"{r['actual_psi_30']:>12.3f}  {r['held_s']:>8.1f}  {r['event']}")
    print("=" * 60)

    if burst_psi:
        print(f"\nBURST PRESSURE: {burst_psi:.2f} PSI")
        rec_target = round(burst_psi * 0.50, 1)   # 50% of burst
        rec_max    = round(burst_psi * 0.65, 1)   # 65% of burst
        rec_warn   = round(burst_psi * 0.60, 1)   # 60% of burst
        print(f"\nRECOMMENDED THRESHOLDS (conservative, ~50-65% of burst):")
        print(f"  TARGET_PRESSURE   = {rec_target}  # PSI")
        print(f"  WARNING_PRESSURE  = {rec_warn}  # PSI")
        print(f"  MAX_SAFE_PRESSURE = {rec_max}  # PSI")
        print(f"\nUpdate these values in:")
        print(f"  balloon_control_api.py    (lines ~41-43)")
        print(f"  balloon_control_secure.py (lines ~52-54)")
    else:
        print("\nNo burst detected — bottle held to test ceiling.")
        print(f"Consider increasing MAX_PRESSURE (currently {MAX_PRESSURE} PSI) for next run.")
    print("=" * 60)


# ── Signal handler ────────────────────────────────────────────────────────────
def _sigint_handler(sig, frame):
    print("\nCtrl+C received — initiating emergency vent...")
    emergency_vent()
    time.sleep(2)
    print_results(results, burst_psi=None)
    sys.exit(0)

# ── Main ──────────────────────────────────────────────────────────────────────

def main(args):
    signal.signal(signal.SIGINT, _sigint_handler)

    start   = args.start
    step    = args.step
    ceiling = args.ceiling
    hold_s  = args.hold

    print("=" * 60)
    print("BURST PRESSURE CHARACTERIZATION TEST")
    print("=" * 60)
    print(f"  Start pressure : {start:.1f} PSI")
    print(f"  Step size      : {step:.1f} PSI")
    print(f"  Hard ceiling   : {ceiling:.1f} PSI  (abort if exceeded)")
    print(f"  Hold per step  : {hold_s} s")
    print(f"  Burst drop     : {BURST_DROP_THRESHOLD:.1f} PSI drop = burst detected")
    print(f"  STACK=0, Relays: pump={RELAY_PUMP} (40A HAT), inflate={RELAY_INFLATE}, "
          f"downstream={RELAY_DOWNSTREAM}, upstream={RELAY_UPSTREAM} (8-relay HAT)")
    print("=" * 60)

    # Safety gate
    confirm = input("\nType 'GO' to begin (all-caps, followed by Enter): ")
    if confirm.strip() != "GO":
        print("Aborted.")
        return 0

    # ── Initialize hardware ──
    chan_a1 = chan_a0 = None

    if SENSOR_AVAILABLE:
        try:
            i2c  = busio.I2C(board.SCL, board.SDA)
            ads  = ADS.ADS1115(i2c)
            chan_a1 = AnalogIn(ads, 1)   # A1 = 100 PSI downstream (primary)
            chan_a0 = AnalogIn(ads, 0)   # A0 = 100 PSI upstream (redundant)
            print("✓ ADS1115 initialized (BSS138 level shifter)")
            print("  chan_a1 = A1 (100 PSI downstream, primary control)")
            print("  chan_a0 = A0 (100 PSI upstream, redundant monitoring)")
        except Exception as e:
            print(f"✗ ADS1115 init failed: {e}")
            print("  Check I2C wiring and BSS138 connections.")
            print("  Run: i2cdetect -y 1  (expect 0x27, 0x48, 0x60)")
            return 1

    if not RELAYS_AVAILABLE:
        print("✗ Relay HATs not available — cannot control hardware.")
        return 1

    # Standardization: vent system to atmospheric pressure
    print("\nStandardization — venting to atmospheric pressure...")
    print("  PUMP OFF...")
    pump_off()
    time.sleep(0.5)  # Let pump fully stop

    print("  Opening all solenoids (inflate, downstream, upstream)...")
    open_inflate()
    open_downstream()
    open_upstream()

    # Wait for pressure to drop to near-zero (max 30 seconds)
    print("  Waiting for pressure to drop to <0.5 PSI...")
    vent_timeout = 30
    vent_start = time.time()
    while True:
        psi_a1, psi_a0 = read_pressures(chan_a1, chan_a0)
        if psi_a1 is not None and psi_a1 < 0.5:
            print(f"  ✓ Vented to {psi_a1:.3f} PSI in {time.time() - vent_start:.1f}s")
            break
        if time.time() - vent_start > vent_timeout:
            print(f"  ⚠ Vent timeout after {vent_timeout}s, pressure still at {psi_a1:.3f} PSI")
            break
        time.sleep(0.5)

    print("  Closing downstream and upstream solenoids...")
    close_downstream()
    close_upstream()
    # Leave inflate valve OPEN for pressurization

    print("  Reading baseline pressure...")
    time.sleep(1)
    psi_a1, psi_a0 = read_pressures(chan_a1, chan_a0)
    if psi_a1 is not None:
        print(f"  Baseline: A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI")
    print("  Standardization complete — ready for test.\n")

    # ── Step loop ────────────────────────────────────────────────────────────
    global pump_running, inflate_open, downstream_open, upstream_open

    burst_psi   = None
    prev_psi_a1 = 0.0
    prev_psi_a0 = 0.0
    target      = start

    # Reset global state variables to match physical state after standardization
    pump_running = False
    inflate_open = True  # Already opened during standardization
    downstream_open = False
    upstream_open = False

    while target <= ceiling:
        print(f"\n{'─'*60}")
        print(f"STEP: Pressurizing to {target:.1f} PSI")
        print(f"{'─'*60}")

        # Both sensors are 100 PSI - use A1 (downstream) as primary control
        print(f"  Inflating to {target:.1f} PSI using pulsed pump control (via A1 sensor)...")

        # Make sure inflate valve is OPEN
        if not inflate_open:
            open_inflate()

        reached_target = False
        pulse_count = 0

        while True:
            # Read current pressure
            psi_a1, psi_a0 = read_pressures(chan_a1, chan_a0)

            if psi_a1 is None:
                emergency_vent()
                return 1

            # Use A1 (downstream) as primary control sensor
            control_psi = psi_a1

            # Hard ceiling check
            if psi_a1 >= ceiling:
                print(f"\n⚠  HARD CEILING REACHED: A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI")
                pump_off()
                emergency_vent()
                results.append({"target_psi": target, "actual_psi_15": psi_a1,
                                 "actual_psi_30": psi_a0, "held_s": 0, "event": "CEILING HIT"})
                print_results(results, burst_psi)
                return 0

            # Burst check - try both sensors
            drop_a1 = prev_psi_a1 - psi_a1
            drop_a0 = prev_psi_a0 - psi_a0
            if (prev_psi_a1 > 1.0 and drop_a1 >= BURST_DROP_THRESHOLD) or \
               (prev_psi_a0 > 1.0 and drop_a0 >= BURST_DROP_THRESHOLD):
                burst_psi = max(prev_psi_a1, prev_psi_a0)
                pump_off()
                emergency_vent()
                results.append({"target_psi": target, "actual_psi_15": psi_a1,
                                 "actual_psi_30": psi_a0, "held_s": 0, "event": "BURST"})
                print(f"\n*** BURST DETECTED at ~{burst_psi:.2f} PSI ***")
                print_results(results, burst_psi)
                return 0

            prev_psi_a1 = psi_a1
            prev_psi_a0 = psi_a0

            # Check if target reached
            if control_psi >= target:
                pump_off()
                reached_target = True
                print(f"  ✓ Reached target: A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI after {pulse_count} pulses")
                break

            # Pulse pump for short duration
            pulse_count += 1
            print(f"    Pulse #{pulse_count}: A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI → pumping {PUMP_PULSE_DURATION}s...")
            pump_on()
            time.sleep(PUMP_PULSE_DURATION)
            pump_off()

            # Wait for pressure to stabilize after pulse
            time.sleep(0.5)

        if not reached_target:
            break

        # Do NOT vent relief valve - keep upstream pressurized
        print(f"  Pump OFF, holding at A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI for {hold_s}s...")

        # ── Hold phase - just monitor for burst, do NOT vent or maintain ──
        hold_start = time.time()

        while True:
            elapsed_hold = time.time() - hold_start
            psi_a1, psi_a0 = read_pressures(chan_a1, chan_a0)

            if psi_a1 is None:
                emergency_vent()
                return 1

            # Hard ceiling check
            if psi_a1 >= ceiling:
                print(f"\n⚠  HARD CEILING during hold: A1={psi_a1:.3f} PSI, A0={psi_a0:.3f} PSI")
                emergency_vent()
                results.append({"target_psi": target, "actual_psi_15": psi_a1,
                                 "actual_psi_30": psi_a0, "held_s": elapsed_hold, "event": "CEILING HIT"})
                print_results(results, burst_psi)
                return 0

            # Burst check - monitor both sensors
            drop_a1 = prev_psi_a1 - psi_a1
            drop_a0 = prev_psi_a0 - psi_a0
            if (prev_psi_a1 > 1.0 and drop_a1 >= BURST_DROP_THRESHOLD) or \
               (prev_psi_a0 > 1.0 and drop_a0 >= BURST_DROP_THRESHOLD):
                burst_psi = max(prev_psi_a1, prev_psi_a0)
                emergency_vent()
                results.append({"target_psi": target, "actual_psi_15": psi_a1,
                                 "actual_psi_30": psi_a0, "held_s": elapsed_hold, "event": "BURST"})
                print(f"\n*** BURST DETECTED at ~{burst_psi:.2f} PSI ***")
                print_results(results, burst_psi)
                return 0

            prev_psi_a1 = psi_a1
            prev_psi_a0 = psi_a0
            print_reading(target, psi_a1, psi_a0, elapsed_hold, hold_s)

            if elapsed_hold >= hold_s:
                # Step held successfully — do NOT vent, move to next step
                results.append({"target_psi": target, "actual_psi_15": psi_a1,
                                 "actual_psi_30": psi_a0, "held_s": elapsed_hold, "event": "OK"})
                print(f"  ✓ Held ~{target:.1f} PSI (A1={psi_a1:.2f} PSI, A0={psi_a0:.2f} PSI) for {hold_s}s")
                break

            time.sleep(POLL_INTERVAL)

        target = round(target + step, 2)

    # ── Test complete — no burst at ceiling ──────────────────────────────────
    print(f"\n✓ Test complete. Bottle survived to {ceiling:.1f} PSI ceiling.")
    print("  Venting system...")

    pump_off()
    time.sleep(0.5)  # Let pump stop before venting
    close_inflate()
    open_downstream()
    open_upstream()
    print("  Venting for 5 seconds...")
    time.sleep(5)
    close_downstream()
    close_upstream()
    close_inflate()  # Ensure inflate valve is also closed
    print("  ✓ Venting complete, all relays off")
    print_results(results, burst_psi=None)
    return 0


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Burst pressure characterization — 1L bottle",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--start",    type=float, default=START_PRESSURE,
                        help="Starting step (PSI)")
    parser.add_argument("--step",     type=float, default=STEP_SIZE,
                        help="Step size (PSI)")
    parser.add_argument("--ceiling",  type=float, default=MAX_PRESSURE,
                        help="Hard abort ceiling (PSI) — will NOT exceed this")
    parser.add_argument("--hold",     type=int,   default=HOLD_SECONDS,
                        help="Hold time at each step (seconds)")
    _args = parser.parse_args()

    sys.exit(main(_args))
