# Balloon Demo - Systemd Service Files

This directory contains systemd service files for automatic startup of balloon control systems.

## Service Files

### Vulnerable System (Pi #7 - 192.168.50.100)

**balloon-sensor-publisher.service**
- Reads BMP388 sensor via I²C
- Publishes pressure data to localhost:5000/sensor via HTTP
- Simulates network-connected IoT sensor
- **Security**: Minimal hardening (intentionally vulnerable)

**balloon-control-api.service**
- Flask API server on port 5000
- Accepts unauthenticated sensor data
- Controls relays based on received pressure readings
- **Security**: No authentication, no validation (intentionally vulnerable)

### Secure System (Pi #6 - 10.30.0.25)

**balloon-control-secure.service**
- Direct I²C sensor reading (no network exposure)
- Wazuh SIEM logging via syslog
- Input validation and anomaly detection
- Attack detection and alerting
- **Security**: Hardened with systemd security features

## Installation Instructions

### For Pi #7 (Vulnerable System)

```bash
# SSH to Pi #7
ssh username@192.168.50.100

# Copy service files to systemd directory
sudo cp balloon-sensor-publisher.service /etc/systemd/system/
sudo cp balloon-control-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services (auto-start on boot)
sudo systemctl enable balloon-sensor-publisher.service
sudo systemctl enable balloon-control-api.service

# Start services now
sudo systemctl start balloon-sensor-publisher.service
sudo systemctl start balloon-control-api.service

# Check status
sudo systemctl status balloon-sensor-publisher.service
sudo systemctl status balloon-control-api.service
```

### For Pi #6 (Secure System)

```bash
# SSH to Pi #6
ssh username@10.30.0.25

# Copy service file to systemd directory
sudo cp balloon-control-secure.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable balloon-control-secure.service

# Start service now
sudo systemctl start balloon-control-secure.service

# Check status
sudo systemctl status balloon-control-secure.service
```

## Viewing Logs

```bash
# View live logs (vulnerable sensor publisher)
sudo journalctl -u balloon-sensor-publisher.service -f

# View live logs (vulnerable control API)
sudo journalctl -u balloon-control-api.service -f

# View live logs (secure system)
sudo journalctl -u balloon-control-secure.service -f

# View logs since last boot
sudo journalctl -u balloon-control-secure.service -b

# View last 100 lines
sudo journalctl -u balloon-control-api.service -n 100
```

## Stopping Services

```bash
# Stop services
sudo systemctl stop balloon-sensor-publisher.service
sudo systemctl stop balloon-control-api.service
sudo systemctl stop balloon-control-secure.service

# Disable auto-start on boot
sudo systemctl disable balloon-sensor-publisher.service
sudo systemctl disable balloon-control-api.service
sudo systemctl disable balloon-control-secure.service
```

## Deployment History

### 2026-02-05 - Initial Deployment

**Successfully deployed all services to both Raspberry Pis.**

**Services Deployed:**
- Pi #7 (192.168.50.100): `balloon-control-api.service` ✅ RUNNING, `balloon-sensor-publisher.service` ⏸️ disabled
- Pi #6 (10.30.0.25): `balloon-control-secure.service` ⏸️ disabled

**Issues Encountered and Resolved:**

1. **CHDIR Permission Denied** (Pi #6)
   - Error: `Failed at step CHDIR spawning /usr/bin/python3: Permission denied`
   - Cause: `ProtectHome=true` prevented access to `/home/username/`
   - Fix: Changed to `ProtectHome=read-only`

2. **GPIO Library Temp File Error** (Pi #6)
   - Error: `FileNotFoundError: .lgd-nfy-3`
   - Cause: `PrivateTmp=true` blocked lgpio library temp file creation
   - Fix: Removed `PrivateTmp=true` from service file

3. **System Directory Access** (Pi #6)
   - Cause: `ProtectSystem=strict` blocked GPIO daemon writes
   - Fix: Removed `ProtectSystem=strict`

4. **GPIO/I2C Group Permissions** (Pi #6)
   - Fix: Added `SupplementaryGroups=gpio i2c` to service file

**Lessons Learned:**
- Hardware control services require relaxed systemd sandboxing
- GPIO/I2C libraries (lgpio, adafruit_blinka) need filesystem and /tmp access
- Security achieved through network isolation, application validation, and SIEM monitoring
- Running as non-root user (`username`) with `NoNewPrivileges=true` provides adequate protection

**Current Status:**
- ✅ Pi #7 control API running and accessible at http://192.168.50.100:5000
- ⏸️ Sensor services disabled until BMP388 hardware arrives
- ⏸️ Secure system disabled until hardware arrives
- 📦 Waiting for: Sequent 8-RELAYS HAT, BMP388 sensors

---

## Troubleshooting

### Service fails to start

1. Check script permissions:
```bash
ls -l /home/username/balloon-demo/scripts/*.py
# Should show: -rwxr-xr-x (executable)
chmod +x /home/username/balloon-demo/scripts/*.py
```

2. Check for Python errors:
```bash
# Run script manually to see errors
cd /home/username/balloon-demo/scripts
python3 balloon_control_api.py
```

3. Check service status:
```bash
sudo systemctl status balloon-control-api.service
```

4. View detailed logs:
```bash
sudo journalctl -u balloon-control-api.service -n 50 --no-pager
```

### Dependencies not installed

If services fail with import errors, install dependencies:

```bash
# BMP388 sensor library
sudo pip3 install adafruit-circuitpython-bmp3xx

# Flask web framework
sudo pip3 install flask

# Requests library (for attack script)
sudo pip3 install requests

# Sequent 8-RELAYS HAT library
cd ~
git clone https://github.com/SequentMicrosystems/8relind-rpi.git
cd 8relind-rpi/python
sudo python3 setup.py install
```

### I²C not enabled

Enable I²C interface:
```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Yes
sudo reboot
```

Check I²C devices:
```bash
i2cdetect -y 1
# Should show:
# - 0x20 (8-RELAYS HAT)
# - 0x77 (BMP388 sensor)
```

## Service Dependencies

**balloon-sensor-publisher.service** requires:
- BMP388 sensor connected via I²C
- `adafruit-circuitpython-bmp3xx` library
- balloon-control-api.service running (publishes to localhost:5000)

**balloon-control-api.service** requires:
- Sequent 8-RELAYS HAT
- `lib8relind` library
- Flask installed
- Port 5000 available

**balloon-control-secure.service** requires:
- BMP388 sensor connected via I²C
- Sequent 8-RELAYS HAT
- `adafruit-circuitpython-bmp3xx` library
- `lib8relind` library
- Syslog available for Wazuh logging

## Security Notes

### Vulnerable System Services
- Intentionally minimal security hardening
- Run as `pi` user (not root, but not heavily restricted)
- `NoNewPrivileges=true` prevents privilege escalation
- No filesystem restrictions (ProtectSystem=false by default)
- Demonstrates poor security practices

### Secure System Service
- Enhanced systemd security features:
  - `NoNewPrivileges=true` - prevent privilege escalation
  - `PrivateTmp=true` - isolated /tmp directory
  - `ProtectSystem=strict` - read-only /usr and /boot
  - `ProtectHome=true` - no access to /home directories
  - `ReadWritePaths=/var/log` - only /var/log is writable
  - `CPUQuota=50%` - resource limits
- Demonstrates security best practices
- Logs all actions to syslog for Wazuh SIEM

## Demo Startup Sequence

For expo demonstrations:

1. **Power on both Raspberry Pis**
2. **Wait 30 seconds** (services auto-start)
3. **Verify vulnerable system** (Pi #7):
   ```bash
   curl http://192.168.50.100:5000/status
   ```
4. **Verify secure system** (Pi #6):
   ```bash
   sudo journalctl -u balloon-control-secure.service -n 20
   ```
5. **Ready for attack demonstration**

## Emergency Stop

If balloon over-inflates during demo:

```bash
# Vulnerable system
curl -X POST http://192.168.50.100:5000/emergency_stop

# Secure system (SSH required)
ssh pi@10.30.0.25
sudo systemctl stop balloon-control-secure.service
```

## File Locations

```
/home/username/balloon-demo/
├── scripts/
│   ├── balloon_control_api.py
│   ├── balloon_control_secure.py
│   ├── sensor_publisher.py
│   ├── attack_spoof.py
│   ├── test_bmp388.py
│   └── test_relays.py
└── services/
    ├── balloon-sensor-publisher.service
    ├── balloon-control-api.service
    ├── balloon-control-secure.service
    └── README.md

/etc/systemd/system/
├── balloon-sensor-publisher.service (symlink)
├── balloon-control-api.service (symlink)
└── balloon-control-secure.service (symlink)
```
