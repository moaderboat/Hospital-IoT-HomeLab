#!/usr/bin/env python3
"""
Balloon Demo - Live Terminal Dashboard
Polls local Flask /status endpoint and displays live system state.

Works on both Pi #6 (Secure) and Pi #7 (Vulnerable) — same script.
Run alongside the control script in a second terminal:
    python3 dashboard.py

Requires: pip3 install rich requests
"""

import time
import requests
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Configuration
API_URL = "http://localhost:5000/status"
REFRESH_RATE = 0.5  # seconds

console = Console()

# Pressure bar settings
BAR_WIDTH = 40
PSI_DISPLAY_MAX = 15.0  # Max PSI shown on gauge (sensor limit)


def psi_bar(pressure, target, max_safe, absolute_max):
    """Render a visual pressure bar with color zones"""
    fill = int((pressure / PSI_DISPLAY_MAX) * BAR_WIDTH)
    fill = max(0, min(fill, BAR_WIDTH))
    empty = BAR_WIDTH - fill

    if pressure >= max_safe:
        color = "bold red"
    elif pressure >= target:
        color = "bold yellow"
    else:
        color = "bold green"

    bar = Text()
    bar.append("[", style="white")
    bar.append("█" * fill, style=color)
    bar.append("░" * empty, style="dim white")
    bar.append("]", style="white")
    return bar


def relay_indicator(state, label):
    """Render a relay ON/OFF indicator"""
    t = Text()
    if state:
        t.append(f"  ● {label}", style="bold green")
    else:
        t.append(f"  ○ {label}", style="dim white")
    return t


def warning_panel(data):
    """Build the warnings/alerts panel based on current state"""
    messages = []

    pressure = data.get("pressure_psi", 0)
    target = data.get("target_pressure", 2.5)
    warning_psi = data.get("warning_pressure", 3.0)
    max_safe = data.get("max_safe_pressure", 3.5)
    absolute_max = data.get("absolute_max_pressure", 4.0)

    if data.get("emergency_stop"):
        messages.append(("bold red", "⚠  EMERGENCY STOP ACTIVE"))

    if data.get("attack_detected"):
        messages.append(("bold red blink", "🚨 ATTACK DETECTED — SPOOFED SENSOR DATA"))
        source = data.get("last_sensor_source", "unknown")
        messages.append(("red", f"   Last sensor source: {source}"))

    if pressure >= absolute_max:
        messages.append(("bold red", f"⚠  ABSOLUTE MAX PRESSURE EXCEEDED: {pressure:.2f} PSI"))
    elif pressure >= max_safe:
        messages.append(("bold red", f"⚠  OVER MAX SAFE PRESSURE: {pressure:.2f} PSI — VENTING"))
    elif pressure >= warning_psi:
        messages.append(("bold yellow", f"⚡ WARNING: High pressure {pressure:.2f} PSI"))

    if data.get("relief_valve_open"):
        messages.append(("bold yellow", "⚠  UPSTREAM RELIEF VALVE OPEN (>25 PSI)"))

    anomalies = data.get("anomaly_count", 0)
    if anomalies > 0:
        messages.append(("yellow", f"   Anomalies detected: {anomalies}"))

    if not messages:
        messages.append(("bold green", "✓  All systems normal"))

    t = Text()
    for style, msg in messages:
        t.append(msg + "\n", style=style)

    return t


def build_dashboard(data, error=None):
    """Build the full dashboard layout"""

    # --- Header ---
    system_name = data.get("system", "Balloon Control System") if data else "Balloon Control System"
    pi_id = data.get("pi", "Unknown Pi") if data else "Unknown Pi"
    vlan = data.get("vlan", "") if data else ""
    timestamp = datetime.now().strftime("%H:%M:%S")

    is_vulnerable = "Vulnerable" in system_name
    header_style = "bold red on black" if is_vulnerable else "bold green on black"
    header_label = "⚠  VULNERABLE SYSTEM" if is_vulnerable else "🔒 SECURE SYSTEM"

    header = Panel(
        Text.assemble(
            (f"{header_label}\n", header_style),
            (f"{pi_id}  |  {vlan}\n", "white"),
            (f"Last update: {timestamp}", "dim white")
        ),
        box=box.DOUBLE,
        border_style="red" if is_vulnerable else "green"
    )

    if error or not data:
        error_panel = Panel(
            Text(f"Cannot connect to control API\n{error or ''}", style="bold red"),
            title="CONNECTION ERROR",
            border_style="red"
        )
        layout = Layout()
        layout.split_column(
            Layout(header, size=7),
            Layout(error_panel)
        )
        return layout

    pressure = data.get("pressure_psi", 0)
    target = data.get("target_pressure", 2.5)
    max_safe = data.get("max_safe_pressure", 3.5)
    absolute_max = data.get("absolute_max_pressure", 4.0)

    # --- Pressure gauge ---
    bar = psi_bar(pressure, target, max_safe, absolute_max)

    if pressure >= max_safe:
        psi_color = "bold red"
    elif pressure >= target:
        psi_color = "bold yellow"
    else:
        psi_color = "bold green"

    gauge_text = Text()
    gauge_text.append(f"\n  {pressure:.4f} PSI\n\n", style=psi_color + " on black")
    gauge_text.append("  ")
    gauge_text.append_text(bar)
    gauge_text.append(f"\n\n  Target:   {target:.1f} PSI\n", style="cyan")
    gauge_text.append(f"  Warning:  {data.get('warning_pressure', 3.0):.1f} PSI\n", style="yellow")
    gauge_text.append(f"  Max Safe: {max_safe:.1f} PSI\n", style="red")

    gauge_panel = Panel(
        gauge_text,
        title="[bold]PRESSURE[/bold]",
        border_style=psi_color,
        box=box.ROUNDED
    )

    # --- Relay states ---
    relay_text = Text()
    relay_text.append("\n")
    relay_text.append_text(relay_indicator(data.get("pump_running"), "Relay 1 — PUMP"))
    relay_text.append("\n")
    relay_text.append_text(relay_indicator(data.get("inflate_valve_open"), "Relay 2 — INFLATE (Sol #1)"))
    relay_text.append("\n")
    relay_text.append_text(relay_indicator(data.get("vent_valve_open"), "Relay 3 — VENT (Sol #2)"))
    relay_text.append("\n")
    relay_text.append_text(relay_indicator(data.get("relief_valve_open"), "Relay 4 — RELIEF (Sol #3)"))
    relay_text.append("\n")

    relay_panel = Panel(
        relay_text,
        title="[bold]RELAY STATES[/bold]",
        border_style="white",
        box=box.ROUNDED
    )

    # --- Stats ---
    stats_table = Table(box=None, show_header=False, padding=(0, 2))
    stats_table.add_column(style="dim white")
    stats_table.add_column(style="white")
    stats_table.add_row("Sensor reads:", str(data.get("sensor_read_count", 0)))
    stats_table.add_row("Anomalies:", str(data.get("anomaly_count", 0)))
    stats_table.add_row("Emergency stops:", str(data.get("emergency_stop_count", 0)))
    if is_vulnerable:
        stats_table.add_row("Last source:", str(data.get("last_sensor_source", "none")))

    stats_panel = Panel(
        stats_table,
        title="[bold]STATISTICS[/bold]",
        border_style="white",
        box=box.ROUNDED
    )

    # --- Warnings ---
    warnings_panel = Panel(
        warning_panel(data),
        title="[bold]ALERTS & WARNINGS[/bold]",
        border_style="red" if (data.get("emergency_stop") or data.get("attack_detected")) else "yellow",
        box=box.ROUNDED
    )

    # --- Layout assembly ---
    layout = Layout()
    layout.split_column(
        Layout(header, name="header", size=7),
        Layout(name="body"),
        Layout(warnings_panel, name="warnings", size=10)
    )
    layout["body"].split_row(
        Layout(gauge_panel, name="gauge"),
        Layout(name="right")
    )
    layout["right"].split_column(
        Layout(relay_panel, name="relays"),
        Layout(stats_panel, name="stats")
    )

    return layout


def main():
    console.clear()

    with Live(console=console, refresh_per_second=int(1 / REFRESH_RATE), screen=True) as live:
        while True:
            try:
                response = requests.get(API_URL, timeout=2)
                data = response.json()
                error = None
            except requests.exceptions.ConnectionError:
                data = None
                error = "Connection refused — is the control script running?"
            except requests.exceptions.Timeout:
                data = None
                error = "Request timed out"
            except Exception as e:
                data = None
                error = str(e)

            live.update(build_dashboard(data, error))
            time.sleep(REFRESH_RATE)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        console.print("[bold green]Dashboard stopped.[/bold green]")
