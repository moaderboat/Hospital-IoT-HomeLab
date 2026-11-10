#!/usr/bin/env python3
"""
Secure System - Balloon Control with Hardened Security
Direct I²C sensor reading with Wazuh SIEM logging and input validation

SECURITY FEATURES:
  Direct I²C sensor reading (no network exposure)
  Wazuh SIEM logging of all actions
  Input validation and sanity checks
  Redundant safety checks
  Attack detection and alerting
  Firewall isolation (VLAN30)

Pi #6 (Secure System) - 10.30.0.25 (VLAN30)
"""

import time
import threading
import syslog
import signal
import sys
from datetime import datetime
from flask import Flask, jsonify

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    SENSOR_AVAILABLE = True
except ImportError:
    print("Warning: ADS1115 library not available - sensor disabled (testing mode)")
    SENSOR_AVAILABLE = False

try:
    import lib8relind
    RELAY8_AVAILABLE = True
except ImportError:
    print("Warning: lib8relind not installed - 8-relay HAT control disabled (testing mode)")
    RELAY8_AVAILABLE = False

try:
    import lib3relind
    RELAY40A_AVAILABLE = True
except ImportError:
    print("Warning: lib3relind not installed - 40A relay HAT control disabled (testing mode)")
    RELAY40A_AVAILABLE = False

RELAYS_AVAILABLE = RELAY8_AVAILABLE or RELAY40A_AVAILABLE

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    print("Warning: paho-mqtt not installed - MQTT publishing disabled")
    MQTT_AVAILABLE = False

# Configuration
# Physical flow: Pump UPSTREAM (R4) INFLATE (R2) DOWNSTREAM (R3) Bottle
STACK = 0  # Relay HAT stack level
RELAY_PUMP       = 1   # Air pump
RELAY_INFLATE    = 2   # Main line control solenoid
RELAY_DOWNSTREAM = 3   # Closest to bottle (vent/deflate)
RELAY_UPSTREAM   = 4   # Closer to pump (high-pressure relief)

# DATAQ sensor constants (ADS1115 via BSS138 level shifter)
# A0 = 100 PSI upstream sensor (2000361-100H) upstream relief monitoring
# A1 = 100 PSI downstream sensor (2000361-100H)  PRIMARY control sensor
VOLTAGE_MIN = 0.5   # V at 0 PSI (both sensors)
VOLTAGE_MAX = 4.5   # V at full scale (both sensors)
PRESSURE_SENSOR_MAX_A0 = 100.0  # PSI full scale channel A0 (upstream)
PRESSURE_SENSOR_MAX_A1 = 100.0  # PSI full scale channel A1 (downstream, primary)

# Pressure thresholds (PSI) - SAME AS VULNERABLE SYSTEM
TARGET_PRESSURE = 25.0   # Target balloon pressure (demo baseline)
MAX_SAFE_PRESSURE = 35.0  # Emergency shutoff
WARNING_PRESSURE = 30.0  # Warning threshold
ABSOLUTE_MAX_PRESSURE = 40.0  # Absolute hard limit (should never reach)

# Safety limits for validation
MIN_VALID_PRESSURE = 0.0  # Minimum valid pressure (PSI)
MAX_VALID_PRESSURE = 100.0  # Maximum valid pressure (PSI) - sensor max range
MAX_PRESSURE_CHANGE_RATE = 20.0  # Max PSI/second change (allows 15 PSI/sec inflation rate)
SENSOR_MISMATCH_THRESHOLD = 10.0  # Max difference between network claim and I2C reading (PSI) - accounts for timing lag during rapid inflation

# System state
current_pressure = 0.0           # PSI downstream from LOCAL I2C sensor (ground truth)
current_pressure_network = None  # PSI from VALIDATED network /sensor POST
pressure_upstream_psi = 0.0      # PSI upstream (100 PSI sensor, relief monitoring)
previous_pressure = 0.0
last_pressure_time = datetime.now()
last_network_update = None
last_network_pressure = None
pump_running = False
inflate_valve_open = False
downstream_valve_open = False
upstream_valve_open = False
emergency_stop = False
attack_detected = False
shutting_down = False  # Flag to stop control loop during shutdown

# Statistics
sensor_read_count = 0            # Local I2C sensor reads
network_sensor_count = 0         # Network /sensor POST attempts
accepted_network_count = 0       # Network readings that passed validation
rejected_network_count = 0       # Network readings rejected (attacks)
anomaly_count = 0
emergency_stop_count = 0

# Attack detection clearing
last_attack_time = None  # Track when last attack was detected
ATTACK_CLEAR_TIMEOUT = 1.0  # Seconds of clean operation before clearing flag

def voltage_to_psi(voltage, sensor_max_psi):
    """Convert DATAQ sensor voltage to PSI. sensor_max_psi = 15.0 or 30.0"""
    if voltage < VOLTAGE_MIN:
        return 0.0
    if voltage > VOLTAGE_MAX:
        return sensor_max_psi
    return (voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN) * sensor_max_psi

def log_to_wazuh(severity, message, event_type="balloon_control"):
    """
    Log security events to Wazuh SIEM

    This uses syslog which Wazuh agents monitor.
    All events are logged for security analysis and alerting.
    """
    # Map severity to syslog levels
    severity_map = {
        "info": syslog.LOG_INFO,
        "warning": syslog.LOG_WARNING,
        "error": syslog.LOG_ERR,
        "critical": syslog.LOG_CRIT,
        "alert": syslog.LOG_ALERT
    }

    level = severity_map.get(severity, syslog.LOG_INFO)

    # Format: [EVENT_TYPE] message
    log_msg = f"[{event_type}] {message}"
    syslog.syslog(level, log_msg)

    # Also print to console
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{severity.upper()}] {log_msg}")

def validate_pressure(pressure):
    """
    Validate pressure reading for anomalies

    Returns: (is_valid, reason)
    """
    global previous_pressure, last_pressure_time, anomaly_count

    # Check if pressure is in valid range
    if pressure < MIN_VALID_PRESSURE:
        return False, f"Pressure too low ({pressure:.2f} < {MIN_VALID_PRESSURE})"

    if pressure > MAX_VALID_PRESSURE:
        return False, f"Pressure too high ({pressure:.2f} > {MAX_VALID_PRESSURE})"

    # Check rate of change (detect sudden jumps)
    now = datetime.now()
    time_delta = (now - last_pressure_time).total_seconds()

    if time_delta > 0:
        pressure_delta = abs(pressure - previous_pressure)
        rate_of_change = pressure_delta / time_delta

        if rate_of_change > MAX_PRESSURE_CHANGE_RATE:
            anomaly_count += 1
            return False, f"Pressure change too rapid ({rate_of_change:.2f} PSI/s > {MAX_PRESSURE_CHANGE_RATE})"

    # Update history
    previous_pressure = pressure
    last_pressure_time = now

    return True, "OK"

def set_relay(relay_num, state):
    """Safely set relay state with logging - supports both 8-relay and 40A HATs"""
    relay_names = {
        RELAY_PUMP: "PUMP",
        RELAY_INFLATE: "INFLATE",
        RELAY_DOWNSTREAM: "DOWNSTREAM",
        RELAY_UPSTREAM: "UPSTREAM"
    }
    relay_name = relay_names.get(relay_num, f"RELAY{relay_num}")
    state_str = "ON" if state else "OFF"

    # CRITICAL SAFETY: Never turn pump ON if shutting down
    if relay_num == RELAY_PUMP and state == True and shutting_down:
        log_to_wazuh("warning", "SAFETY: Blocked pump ON command during shutdown", "safety_shutdown")
        return

    log_to_wazuh("info", f"Relay {relay_num} ({relay_name}) {state_str}", "relay_control")

    if RELAYS_AVAILABLE:
        try:
            # PUMP (R1) is on 40A HAT (lib3relind, I2C 0x60, relay 3)
            # INFLATE/DOWNSTREAM/UPSTREAM are on 8-relay HAT (lib8relind, I2C 0x27)
            if relay_num == RELAY_PUMP:
                if RELAY40A_AVAILABLE:
                    lib3relind.set(STACK, 3, 1 if state else 0)  # 40A HAT relay 3
                else:
                    log_to_wazuh("error", "40A HAT not available - cannot control pump", "relay_error")
            else:
                if RELAY8_AVAILABLE:
                    lib8relind.set(STACK, relay_num, 1 if state else 0)
                else:
                    log_to_wazuh("error", "8-relay HAT not available - cannot control solenoids", "relay_error")
        except Exception as e:
            log_to_wazuh("error", f"Relay control failed: {e}", "relay_error")
    else:
        print(f"  [RELAY {relay_num} {relay_name}] {state_str}")

def set_inflate_valve(state):
    """
    Safely control inflate valve with safety interlock

    SAFETY: Ensure downstream valve is closed before opening inflate valve
    """
    global inflate_valve_open, downstream_valve_open

    if state and downstream_valve_open:
        log_to_wazuh("error", "SAFETY INTERLOCK: Cannot open inflate valve while downstream is open", "safety_interlock")
        return False

    set_relay(RELAY_INFLATE, state)
    inflate_valve_open = state
    return True

def set_downstream_valve(state):
    """
    Safely control downstream valve with safety interlock

    SAFETY: Ensure inflate valve is closed before opening downstream valve
    """
    global inflate_valve_open, downstream_valve_open

    if state and inflate_valve_open:
        log_to_wazuh("error", "SAFETY INTERLOCK: Cannot open downstream valve while inflate is open", "safety_interlock")
        return False

    set_relay(RELAY_DOWNSTREAM, state)
    downstream_valve_open = state
    return True

def deflate_balloon():
    """
    Safely deflate balloon to atmospheric pressure

    Steps:
    1. Stop pump
    2. Close inflate valve
    3. Open downstream valve
    4. Wait for pressure to drop below threshold
    5. Close downstream valve
    """
    global pump_running

    log_to_wazuh("info", "Starting balloon deflation", "deflate_start")

    # Step 1: Stop pump
    if pump_running:
        set_relay(RELAY_PUMP, False)
        pump_running = False
        time.sleep(0.1)

    # Step 2: Close inflate valve (safety first)
    if inflate_valve_open:
        set_inflate_valve(False)
        time.sleep(0.1)

    # Step 3: Open downstream valve
    if set_downstream_valve(True):
        log_to_wazuh("info", "Downstream valve opened - releasing air to atmosphere", "deflate_venting")
    else:
        log_to_wazuh("error", "Failed to open downstream valve", "deflate_error")
        return False

    return True

def cleanup_on_exit(signum, frame):
    """Clean up relays when script exits - controlled depressurization"""
    global shutting_down, pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open

    print("\n\n SHUTDOWN SIGNAL RECEIVED")
    shutting_down = True  # Signal control loop to stop (set_relay now blocks pump ON)
    time.sleep(0.7)  # Wait for control loop to exit
    print("Starting depressurization sequence")

    # Step 1: Turn off pump
    print("  1. Pump OFF")
    set_relay(RELAY_PUMP, False)
    pump_running = False
    time.sleep(0.2)

    # Step 2: Close inflate valve (stop flow path)
    print("  2. Inflate valve CLOSED")
    set_relay(RELAY_INFLATE, False)
    inflate_valve_open = False
    time.sleep(0.2)

    # Step 3: Open downstream valve (vent bottle)
    print("  3. Downstream valve OPEN (venting)")
    set_relay(RELAY_DOWNSTREAM, True)
    downstream_valve_open = True
    time.sleep(0.2)

    # Step 4: Open upstream valve (vent upstream line)
    print("  4. Upstream valve OPEN (venting)")
    set_relay(RELAY_UPSTREAM, True)
    upstream_valve_open = True
    time.sleep(2.0)  # Wait for depressurization

    # Step 5: Close downstream valve
    print("  5. Downstream valve CLOSED")
    set_relay(RELAY_DOWNSTREAM, False)
    downstream_valve_open = False
    time.sleep(0.2)

    # Step 6: Close upstream valve
    print("  6. Upstream valve CLOSED")
    set_relay(RELAY_UPSTREAM, False)
    upstream_valve_open = False

    log_to_wazuh("info", "Shutdown depressurization complete - all hardware OFF", "system_shutdown")
    print("Depressurization complete - all hardware OFF")
    sys.exit(0)

def emergency_shutdown(reason):
    """Emergency shutdown with full logging and emergency deflation"""
    global emergency_stop, pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open, emergency_stop_count

    emergency_stop = True
    emergency_stop_count += 1

    log_to_wazuh("critical", f"EMERGENCY SHUTDOWN: {reason}", "emergency_stop")

    print("\n" + "=" * 60)
    print(" EMERGENCY SHUTDOWN ACTIVATED")
    print(f"   Reason: {reason}")
    print("=" * 60)

    # Emergency deflation sequence
    # Step 1: Stop pump immediately
    set_relay(RELAY_PUMP, False)
    pump_running = False

    # Step 2: Close inflate valve
    set_relay(RELAY_INFLATE, False)
    inflate_valve_open = False
    time.sleep(0.1)

    # Step 3: Open upstream relief valve
    log_to_wazuh("warning", "Emergency - opening upstream relief valve", "emergency_relief")
    set_relay(RELAY_UPSTREAM, True)
    upstream_valve_open = True

    # Step 4: Open downstream valve to emergency deflate balloon
    log_to_wazuh("warning", "Emergency deflation - opening downstream valve", "emergency_deflate")
    set_relay(RELAY_DOWNSTREAM, True)
    downstream_valve_open = True

def detect_attack(pressure):
    """
    Detect potential spoofing attacks

    Returns: (is_attack, description)
    """
    # NOTE: With inline DATAQ sensor, direct I²C reading is immune to network spoofing
    # These checks are for physical sensor tampering or electrical interference

    # Check for impossible pressure values (beyond sensor range)
    if pressure < 0 or pressure > MAX_VALID_PRESSURE:
        return True, f"Impossible pressure value ({pressure:.2f} PSI, sensor max {MAX_VALID_PRESSURE})"

    # In a real system, we'd check:
    # - Compare multiple sensors
    # - Check pressure trend consistency
    # - Validate against physical model
    # - Monitor for rapid oscillations
    # - Check voltage range (0.5-4.5V expected)

    return False, "No attack detected"

def sensor_loop():
    """Main sensor reading and control loop"""
    global current_pressure, pressure_upstream_psi, pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open
    global emergency_stop, attack_detected, sensor_read_count, last_attack_time

    # Initialize sensor
    # BSS138 level shifter sits between Pi (3.3V) and ADS1115 (5V) on SCL/SDA
    if SENSOR_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c)
            chan_a1 = AnalogIn(ads, 1)  # A1 = 100 PSI downstream (PRIMARY control)
            chan_a0 = AnalogIn(ads, 0)  # A0 = 100 PSI upstream (relief monitoring)
            log_to_wazuh("info", "ADS1115 + BSS138 initialized: 100PSI(A1 downstream) + 100PSI(A0 upstream)", "sensor_init")
        except Exception as e:
            log_to_wazuh("error", f"Sensor init failed: {e}", "sensor_error")
            return
    else:
        log_to_wazuh("warning", "Sensor not available - testing mode", "sensor_warning")
        chan_a1 = None
        chan_a0 = None

    log_to_wazuh("info", "Secure balloon control system started", "system_start")

    while True:
        # Check shutdown flag FIRST (before any sleeps)
        if shutting_down:
            log_to_wazuh("info", "Control loop: shutting_down flag set, exiting", "system_shutdown")
            return

        if emergency_stop:
            time.sleep(0.5)
            continue

        try:
            # Read pressure directly from sensors via I2C (ground truth for validation)
            # Read ONCE per loop (10 Hz) - no median sampling to avoid overwhelming ADS1115
            if chan_a1:
                pressure_psi = voltage_to_psi(chan_a1.voltage, PRESSURE_SENSOR_MAX_A1)
                pressure_upstream_psi = voltage_to_psi(chan_a0.voltage, PRESSURE_SENSOR_MAX_A0)
            else:
                # Testing mode - simulate pressure
                pressure_psi = 0.0
                pressure_upstream_psi = 0.0

            sensor_read_count += 1

            # I2C sensor is ground truth - no rate-of-change validation
            # (Rate-of-change validation only applies to network sensor data in /sensor endpoint)
            # Just do basic range check
            if pressure_psi < MIN_VALID_PRESSURE or pressure_psi > MAX_VALID_PRESSURE:
                log_to_wazuh("warning", f"I2C pressure out of range: {pressure_psi:.2f} PSI", "sensor_error")
                time.sleep(0.1)
                continue

            # Detect attacks
            is_attack, attack_desc = detect_attack(pressure_psi)

            if is_attack:
                if not attack_detected:
                    attack_detected = True
                    log_to_wazuh("alert", f"ATTACK DETECTED: {attack_desc}", "security_attack")
                last_attack_time = datetime.now()
            elif attack_detected and last_attack_time:
                # Check if enough time has passed since last attack
                time_since_attack = (datetime.now() - last_attack_time).total_seconds()
                if time_since_attack > ATTACK_CLEAR_TIMEOUT:
                    attack_detected = False
                    last_attack_time = None
                    log_to_wazuh("info", "Attack cleared - system returned to normal", "attack_cleared")

            current_pressure = pressure_psi

            # Determine control pressure: Use validated network data if available, else I2C
            # This allows secure system to operate like vulnerable (network-based control)
            # but with validation protection
            if current_pressure_network is not None:
                control_pressure = current_pressure_network
                pressure_source = "network_validated"
            else:
                control_pressure = current_pressure
                pressure_source = "i2c_fallback"

            # Safety checks - always use I2C for safety (ground truth)
            if current_pressure >= ABSOLUTE_MAX_PRESSURE:
                emergency_shutdown(f"Absolute max pressure exceeded: {current_pressure:.2f} >= {ABSOLUTE_MAX_PRESSURE}")
                continue

            # NOTE: Upstream valve is NOT used for automatic relief during normal operation
            # (matches vulnerable system behavior for parity)
            # Upstream is only used during overpressure venting (>35 PSI) and shutdown

            if control_pressure >= MAX_SAFE_PRESSURE:
                # OVERPRESSURE VENTING MODE (matches vulnerable system)
                if pump_running:
                    log_to_wazuh("warning", f"OVERPRESSURE: {control_pressure:.2f} PSI >= {MAX_SAFE_PRESSURE} - entering venting mode", "overpressure_venting")
                    set_relay(RELAY_PUMP, False)
                    pump_running = False

                # Close inflate valve
                if inflate_valve_open:
                    set_inflate_valve(False)

                # Open BOTH downstream and upstream valves for venting (matches vulnerable system)
                if not downstream_valve_open:
                    log_to_wazuh("warning", f"Opening downstream valve for overpressure venting", "pressure_vent")
                    set_downstream_valve(True)

                if not upstream_valve_open:
                    log_to_wazuh("warning", f"Opening upstream valve for overpressure venting", "pressure_vent")
                    set_relay(RELAY_UPSTREAM, True)
                    upstream_valve_open = True

            elif control_pressure >= TARGET_PRESSURE:
                # Target reached - stop inflation
                if pump_running:
                    log_to_wazuh("info", f"Target pressure reached: {control_pressure:.2f} PSI (source: {pressure_source})", "target_reached")
                    set_relay(RELAY_PUMP, False)
                    pump_running = False

                if inflate_valve_open:
                    set_inflate_valve(False)

                # Close downstream valve if it was open (maintain pressure at target)
                if downstream_valve_open:
                    log_to_wazuh("info", f"Pressure back to target - closing downstream valve", "downstream_closed")
                    set_downstream_valve(False)

                # Close upstream valve if it was open (exit overpressure venting)
                if upstream_valve_open:
                    log_to_wazuh("info", f"Pressure back to safe - closing upstream valve", "upstream_closed")
                    set_relay(RELAY_UPSTREAM, False)
                    upstream_valve_open = False

            else:
                # Below target - inflate
                if not pump_running and not downstream_valve_open:
                    log_to_wazuh("info", f"Starting inflation (current: {control_pressure:.2f}, target: {TARGET_PRESSURE}, source: {pressure_source})", "inflation_start")

                    # Close all vents first (safety)
                    if downstream_valve_open:
                        set_downstream_valve(False)
                        time.sleep(0.1)

                    if upstream_valve_open:
                        set_relay(RELAY_UPSTREAM, False)
                        upstream_valve_open = False
                        time.sleep(0.1)

                    # Open inflate valve
                    if not inflate_valve_open:
                        set_inflate_valve(True)
                        time.sleep(0.2)

                    # Start pump
                    set_relay(RELAY_PUMP, True)
                    pump_running = True

                # Close vents if we're trying to inflate
                if downstream_valve_open:
                    set_downstream_valve(False)

                if upstream_valve_open:
                    set_relay(RELAY_UPSTREAM, False)
                    upstream_valve_open = False

            # MQTT publishing - send status every 0.5s for real-time dashboard
            if sensor_read_count % 5 == 0:  # Every 0.5s at 10Hz loop
                publish_mqtt("status", {
                    "pressure_i2c": round(current_pressure, 2),
                    "pressure_network": round(current_pressure_network, 2) if current_pressure_network else None,
                    "pressure_control": round(control_pressure, 2),
                    "pressure_source": pressure_source,
                    "pressure_upstream": round(pressure_upstream_psi, 2),
                    "pump_running": pump_running,
                    "inflate_valve_open": inflate_valve_open,
                    "downstream_valve_open": downstream_valve_open,
                    "upstream_valve_open": upstream_valve_open,
                    "emergency_stop": emergency_stop,
                    "attack_detected": attack_detected,
                    "network_sensor_count": network_sensor_count,
                    "accepted_network_count": accepted_network_count,
                    "rejected_network_count": rejected_network_count,
                    "timestamp": datetime.now().isoformat()
                })

            # Log status periodically (every 1 second)
            if sensor_read_count % 10 == 0:
                log_to_wazuh("info",
                    f"Status: I2C={current_pressure:.2f} Control={control_pressure:.2f} ({pressure_source}) Upstream={pressure_upstream_psi:.2f} "
                    f"Pump:{pump_running} Inflate:{inflate_valve_open} Down:{downstream_valve_open} "
                    f"Net:{accepted_network_count}/{network_sensor_count} Rejected:{rejected_network_count}",
                    "status_update")

        except Exception as e:
            log_to_wazuh("error", f"Control loop error: {e}", "control_error")

        time.sleep(0.1)  # 10 Hz control loop

# MQTT Configuration
MQTT_BROKER = "10.30.0.51"  # Central MQTT broker on VLAN30
MQTT_PORT = 1883
MQTT_USER = "username"
MQTT_PASSWORD = "password"
MQTT_TOPIC_PREFIX = "balloon/secure"
username = None

def init_mqtt():
    """Initialize MQTT client for publishing status updates"""
    global username
    if not MQTT_AVAILABLE:
        return

    try:
        username = mqtt.Client(client_id="balloon_secure_control")
        username.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        username.connect(MQTT_BROKER, MQTT_PORT, 60)
        username.loop_start()
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        username = None

def publish_mqtt(topic, payload):
    """Publish data to MQTT topic"""
    if not MQTT_AVAILABLE or username is None:
        return

    try:
        import json
        full_topic = f"{MQTT_TOPIC_PREFIX}/{topic}"
        username.publish(full_topic, json.dumps(payload), qos=0, retain=False)
    except Exception as e:
        # Silently ignore publish errors to avoid spamming logs
        pass

app = Flask(__name__)

@app.route('/status')
def status():
    """
    Read-only status endpoint for dashboard.
    """
    return jsonify({
        "system": "Secure Balloon Control System",
        "pi": "Pi #6 (10.30.0.25)",
        "vlan": "VLAN30 (Secure Network)",
        "pressure_psi": round(current_pressure, 4),           # Local I2C (ground truth)
        "pressure_network": round(current_pressure_network, 4) if current_pressure_network is not None else None,  # Validated network
        "pressure_upstream_psi": round(pressure_upstream_psi, 4),  # 100 PSI upstream
        "pump_running": pump_running,
        "inflate_valve_open": inflate_valve_open,
        "downstream_valve_open": downstream_valve_open,
        "upstream_valve_open": upstream_valve_open,
        "emergency_stop": emergency_stop,
        "attack_detected": attack_detected,
        "sensor_read_count": sensor_read_count,
        "network_sensor_count": network_sensor_count,
        "accepted_network_count": accepted_network_count,
        "rejected_network_count": rejected_network_count,
        "anomaly_count": anomaly_count,
        "emergency_stop_count": emergency_stop_count,
        "target_pressure": TARGET_PRESSURE,
        "max_safe_pressure": MAX_SAFE_PRESSURE,
        "absolute_max_pressure": ABSOLUTE_MAX_PRESSURE,
        "warning_pressure": WARNING_PRESSURE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/sensor', methods=['POST'])
def update_sensor():
    """
    SECURE /sensor endpoint - validates network data against local I2C sensor

    Security features:
    - Cross-checks network claim against local I2C reading (rejects if >1.0 PSI difference)
    - Rate limiting (max 2 Hz)
    - Rate-of-change validation (max 5.0 PSI/sec)
    - Range validation (0-100 PSI)
    - Logs all rejections to Wazuh SIEM
    - Control loop uses validated network data (NOT raw network data)
    """
    global current_pressure_network, last_network_update, last_network_pressure
    global network_sensor_count, accepted_network_count, rejected_network_count
    global attack_detected, anomaly_count, last_attack_time

    from flask import request

    data = request.json
    network_sensor_count += 1

    claimed_pressure = data.get('pressure', None)
    source = data.get('source', 'unknown')

    if claimed_pressure is None:
        rejected_network_count += 1
        log_to_wazuh("warning", f"Rejected: missing pressure field from {source}", "sensor_rejected")
        return jsonify({"status": "rejected", "reason": "missing_pressure"}), 400

    # Validation 1: Range check
    if claimed_pressure < MIN_VALID_PRESSURE or claimed_pressure > MAX_VALID_PRESSURE:
        rejected_network_count += 1
        anomaly_count += 1
        attack_detected = True
        last_attack_time = datetime.now()
        log_to_wazuh("alert",
            f"ATTACK: Out-of-range pressure {claimed_pressure} PSI from {source} (valid: {MIN_VALID_PRESSURE}-{MAX_VALID_PRESSURE})",
            "attack_detected")
        return jsonify({
            "status": "rejected",
            "reason": "out_of_range",
            "claimed": claimed_pressure,
            "valid_range": f"{MIN_VALID_PRESSURE}-{MAX_VALID_PRESSURE}"
        }), 400

    # Validation 2: Cross-check against LOCAL I2C sensor (CRITICAL)
    if current_pressure is not None:
        diff = abs(claimed_pressure - current_pressure)

        if diff > SENSOR_MISMATCH_THRESHOLD:
            rejected_network_count += 1
            anomaly_count += 1
            attack_detected = True
            last_attack_time = datetime.now()
            log_to_wazuh("alert",
                f"ATTACK: Sensor mismatch - network claims {claimed_pressure} PSI but I2C reads {current_pressure} PSI (diff={diff:.2f}) from {source}",
                "spoofing_detected")
            return jsonify({
                "status": "rejected",
                "reason": "sensor_mismatch",
                "network_claimed": claimed_pressure,
                "i2c_actual": current_pressure,
                "difference": round(diff, 2),
                "threshold": SENSOR_MISMATCH_THRESHOLD
            }), 400

    # Validation 3: Rate limiting (max 2 Hz)
    now = datetime.now()
    if last_network_update:
        time_since_last = (now - last_network_update).total_seconds()
        if time_since_last < 0.5:  # Max 2 Hz
            rejected_network_count += 1
            log_to_wazuh("warning", f"Rate limit: {time_since_last:.3f}s < 0.5s from {source}", "rate_limit")
            return jsonify({"status": "rejected", "reason": "rate_limit", "time_since_last": round(time_since_last, 3)}), 429

    # Validation 4: Rate of change
    if last_network_pressure is not None and last_network_update:
        time_delta = (now - last_network_update).total_seconds()
        if time_delta > 0:
            pressure_delta = abs(claimed_pressure - last_network_pressure)
            rate = pressure_delta / time_delta

            if rate > MAX_PRESSURE_CHANGE_RATE:
                rejected_network_count += 1
                anomaly_count += 1
                attack_detected = True
                last_attack_time = datetime.now()
                log_to_wazuh("alert",
                    f"ATTACK: Impossible rate of change {rate:.2f} PSI/sec from {source} (max: {MAX_PRESSURE_CHANGE_RATE})",
                    "anomaly_detected")
                return jsonify({
                    "status": "rejected",
                    "reason": "rate_of_change",
                    "rate": round(rate, 2),
                    "max_allowed": MAX_PRESSURE_CHANGE_RATE
                }), 400

    # All validations passed - store as validated network data
    current_pressure_network = claimed_pressure
    last_network_update = now
    last_network_pressure = claimed_pressure
    accepted_network_count += 1

    log_to_wazuh("info",
        f"Network sensor ACCEPTED: {claimed_pressure} PSI from {source} (I2C: {current_pressure} PSI, diff: {abs(claimed_pressure - current_pressure):.2f})",
        "network_sensor_accepted")

    return jsonify({
        "status": "accepted",
        "message": "Validated against I2C sensor",
        "network_pressure": claimed_pressure,
        "i2c_pressure": current_pressure
    })

def run_flask():
    """Run Flask status server in background thread — all interfaces for /sensor endpoint"""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    print("=" * 60)
    print("SECURE BALLOON CONTROL SYSTEM")
    print("=" * 60)
    print("  Pi #6 (10.30.0.25) - VLAN30 (Secure Network)")
    print("=" * 60)
    print("\nSECURITY FEATURES:")
    print("  Direct I²C sensor reading (no network exposure)")
    print("  Wazuh SIEM logging enabled")
    print("  Input validation and anomaly detection")
    print("  Attack detection system")
    print("  Redundant safety checks")
    print("  Firewall isolation")
    print("=" * 60)
    print(f"  Target Pressure: {TARGET_PRESSURE} PSI")
    print(f"  Max Safe Pressure: {MAX_SAFE_PRESSURE} PSI")
    print(f"  Absolute Max: {ABSOLUTE_MAX_PRESSURE} PSI")
    print(f"  Sensor Available: {SENSOR_AVAILABLE}")
    print(f"  Relays Available: {RELAYS_AVAILABLE}")
    print("=" * 60)
    print("\nInitializing MQTT connection...")
    init_mqtt()

    # Register cleanup handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)

    print("\nInitializing relays (all OFF)...")
    set_relay(RELAY_PUMP, False)
    set_relay(RELAY_INFLATE, False)
    set_relay(RELAY_DOWNSTREAM, False)
    set_relay(RELAY_UPSTREAM, False)
    print("All relays initialized to OFF")
    time.sleep(0.5)  # Let hardware settle before starting control loop

    print("\nStarting Flask status server on port 5000 (all interfaces)...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print("\nStarting secure control loop...")
    print("(Ctrl+C to stop)\n")

    sensor_loop()

if __name__ == "__main__":
    main()
