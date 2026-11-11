# ECG-style heartbeat sweep for Sense HAT (Raspberry Pi)
# Shows a static red "2" with the ECG trace drawn IN FRONT of it.
# pip install sense-hat paho-mqtt
# Run with: python3 HeartRate2Monitor.py

import time, math, sys, json, random
from datetime import datetime
try:
    from sense_hat import SenseHat
except ImportError:
    print("This script requires the sense-hat package and hardware.")
    sys.exit(1)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("This script requires paho-mqtt: pip3 install paho-mqtt")
    sys.exit(1)

# ---------------- Settings ----------------
BPM = 68                 # beats per minute (normal resting)
TRACE = (0, 255, 0)      # ECG trace color (bright green)
TRACE_DIM = (0, 48, 0)   # optional trailing pixel
ONE = (255, 0, 0)        # color of the "2"
BG = (0, 0, 0)           # background

SAMPLES_PER_BEAT = 120   # more = smoother shape
SWEEP_RATE = 60          # columns/second target
SHOW_GRID = True         # faint grid background like a monitor
GRID_GAP = 2             # grid spacing in pixels

# MQTT Settings
MQTT_BROKER = "10.30.0.51"
MQTT_PORT = 1883
MQTT_TOPIC = "hospital/heartrate/pi2"
PI_ID = 2
PUBLISH_INTERVAL = 0.05  # seconds between MQTT publishes (50ms = 20 Hz)

# ------------------------------------------
sense = SenseHat()
sense.low_light = False
sense.clear()

# Setup MQTT
username = mqtt.Client(client_id=f"heartrate_pi{PI_ID}")
mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print(f"[MQTT] Connected to broker at {MQTT_BROKER}")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print(f"[MQTT] Disconnected from broker")

username.on_connect = on_connect
username.on_disconnect = on_disconnect

try:
    username.connect(MQTT_BROKER, MQTT_PORT, 60)
    username.loop_start()
    print(f"[MQTT] Connecting to broker at {MQTT_BROKER}:{MQTT_PORT}...")
except Exception as e:
    print(f"[MQTT] Failed to connect: {e}")
    print("[MQTT] Continuing without MQTT...")

def base_grid():
    if not SHOW_GRID:
        return [BG for _ in range(64)]
    grid = []
    dim = (0, 32, 0)
    for y in range(8):
        for x in range(8):
            if x % GRID_GAP == 0 or y % GRID_GAP == 0:
                grid.append(dim)
            else:
                grid.append(BG)
    return grid

def put_point(pixels, x, y, color):
    if 0 <= x < 8 and 0 <= y < 8:
        pixels[y*8 + x] = color

def draw_digit_one(pixels, color):
    """
    Draw a simple '2' that's readable on 8x8:
      - vertical stroke at x=2 for rows 1..6
      - small base at bottom (x=1..3, y=6)
      - small 'cap' at top (x=2, y=0..1) for readability
    Adjust if you prefer a different shape.
    """
    # hat point
    put_point(pixels, 2, 0, color)
    put_point(pixels, 3, 0, color)
    put_point(pixels, 4, 0, color)
    put_point(pixels, 5, 0, color)
    put_point(pixels, 6, 0, color)
    put_point(pixels, 6, 1, color)
    put_point(pixels, 6, 2, color)
    put_point(pixels, 6, 2, color)
    put_point(pixels, 5, 2, color)
    put_point(pixels, 4, 2, color)
    put_point(pixels, 3, 2, color)
    put_point(pixels, 2, 2, color)
    put_point(pixels, 2, 3, color)
    put_point(pixels, 2, 4, color)
    put_point(pixels, 3, 4, color)
    put_point(pixels, 4, 4, color)
    put_point(pixels, 5, 4, color)
    put_point(pixels, 6, 4, color)

# --- ECG model ---
def ecg_wave(t):
    # Segment durations (proportion of beat)
    p_dur   = 0.08
    pr_dur  = 0.07
    qrs_dur = 0.06
    st_dur  = 0.10
    t_dur   = 0.16

    p_center   = p_dur * 0.5
    qrs_center = p_dur + pr_dur + qrs_dur * 0.45
    t_start    = p_dur + pr_dur + qrs_dur + st_dur
    t_center   = t_start + t_dur * 0.5

    p_amp   = 0.18
    qrs_amp = 1.00
    t_amp   = 0.35
    baseline = 0.05

    def gauss(x, mu, sigma):
        return math.exp(-0.5 * ((x - mu) / sigma)**2)

    val = 0.0
    if 0 <= t < p_dur:  # P
        val += p_amp * gauss(t, p_center, p_dur/4.0)
    # PR (baseline) adds nothing

    # QRS (sharp spike)
    if (p_dur + pr_dur) <= t < (p_dur + pr_dur + qrs_dur):
        tri_pos = (t - (p_dur + pr_dur)) / qrs_dur
        tri = 1.0 - abs(2.0 * tri_pos - 1.0)
        val += qrs_amp * (0.75 * tri + 0.25 * gauss(t, qrs_center, qrs_dur/9.0))

    # ST segment (slightly above baseline)
    if (p_dur + pr_dur + qrs_dur) <= t < (p_dur + pr_dur + qrs_dur + st_dur):
        val += baseline

    # T wave
    if t_start <= t < (t_start + t_dur):
        val += t_amp * gauss(t, t_center, t_dur/3.0)

    return max(0.0, min(1.0, val))

def make_beat_table(bpm, n_samples):
    return [ecg_wave(i / n_samples) for i in range(n_samples)]

def amp_to_row(a):
    # Map amplitude [0..1] to row [1..6] to avoid edge clipping; invert (row 0 is top)
    min_row, max_row = 6, 1
    y = round(min_row + (max_row - min_row) * a)
    return int(max(0, min(7, y)))

# ---- Trace buffer (transparent) ----
# We keep a 64-length list of Optional[tuple] where None = transparent
def trace_clear():
    return [None for _ in range(64)]

def trace_shift_left(trace):
    new_trace = [None for _ in range(64)]
    for y in range(8):
        for x in range(7):  # pixels at x=0..6 move left into x=0..5
            src_idx = y*8 + (x+1)
            dst_idx = y*8 + x
            new_trace[dst_idx] = trace[src_idx]
        # last column becomes transparent
    return new_trace

def composite_frame(base, trace):
    out = base[:]  # copy
    for i, px in enumerate(trace):
        if px is not None:
            out[i] = px
    return out

def run(bpm):
    # Build constant base layer: grid + static red "2"
    BASE = base_grid()
    draw_digit_one(BASE, ONE)

    # Natural heart rate variability (HRV)
    base_bpm = bpm
    current_bpm = bpm
    target_bpm = bpm
    last_hrv_change = time.perf_counter()

    period = 60.0 / current_bpm
    beat = make_beat_table(current_bpm, SAMPLES_PER_BEAT)

    col_dt = 1.0 / SWEEP_RATE  # time between left shifts

    # Trace layer starts transparent
    trace = trace_clear()

    phase = 0.0
    t_prev = time.perf_counter()
    last_publish = time.perf_counter()

    try:
        while True:
            now = time.perf_counter()
            dt = now - t_prev
            if dt < col_dt:
                time.sleep(col_dt - dt)
                now = time.perf_counter()
                dt = now - t_prev
            t_prev = now

            # Natural heart rate variability - subtle drift
            if abs(current_bpm - target_bpm) > 0.1:
                # Very slow drift (1% per update)
                current_bpm += (target_bpm - current_bpm) * 0.01
                period = 60.0 / current_bpm

            # Change target BPM every 4-10 seconds with small variation
            if (now - last_hrv_change) > random.uniform(4.0, 10.0):
                # Vary by ±3.5 BPM around base (most variable of the three)
                target_bpm = base_bpm + random.uniform(-3.5, 3.5)
                last_hrv_change = now

            # Advance ECG phase by real time
            phase = (phase + dt / period) % 1.0
            idx = int(phase * SAMPLES_PER_BEAT) % SAMPLES_PER_BEAT
            a = beat[idx]
            row = amp_to_row(a)

            # Shift only the TRACE layer left
            trace = trace_shift_left(trace)

            # Draw new ECG column at x=7 on trace layer
            # Bright point
            put_point(trace, 7, row, TRACE)
            # Optional trailing pixel to thicken the trace
            if row + 1 <= 7:
                put_point(trace, 7, row + 1, TRACE_DIM)

            # Composite: base (with red "2") + trace (on top)
            frame = composite_frame(BASE, trace)
            sense.set_pixels(frame)

            # Publish MQTT message periodically
            if mqtt_connected and (now - last_publish) >= PUBLISH_INTERVAL:
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "pi_id": PI_ID,
                    "bpm": int(current_bpm),
                    "status": "normal",
                    "anomaly_type": None
                }
                username.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
                last_publish = now

    except KeyboardInterrupt:
        sense.clear()
        username.loop_stop()
        username.disconnect()
        print("\nStopped.")

if __name__ == "__main__":
    print(f"Starting ECG sweep at {BPM} bpm with static red '1'. Press Ctrl+C to stop.")
    run(BPM)
