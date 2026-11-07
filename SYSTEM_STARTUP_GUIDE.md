# Hospital Homelab System Startup Guide

**Purpose:** Complete reference for bringing up the entire hospital homelab from a powered-down state.

**Last Updated:** 2026-03-23

---

## 📋 Quick Reference: SSH Credentials

### Virtual Machines (All VMs on TrueNAS 10.30.0.44)

| System | IP Address | SSH Command | Username | Password | Web Access |
|--------|------------|-------------|----------|----------|------------|
| **TrueNAS Host** | 10.30.0.44 | `ssh username@10.30.0.44` | `username` | `password` | http://10.30.0.44 |
| **PostgreSQL** | 10.30.0.50 | `ssh username@10.30.0.50` | `username` | `password` | N/A (database only) |
| **MQTT Broker** | 10.30.0.51 | `ssh username@10.30.0.51` | `username` | `password` | N/A (MQTT port 1883) |
| **Node-RED** | 10.30.0.52 | `ssh username@10.30.0.52` | `username` | `password` | http://10.30.0.52:1880 |
| **Grafana** | 10.30.0.53 | `ssh username@10.30.0.53` | `username` | `password` | http://10.30.0.53:3000 |
| **Mirth Connect** | 10.30.0.54 | `ssh username@10.30.0.54` | `username` | `password` | https://10.30.0.54:8443 |
| **Wazuh SIEM** | 10.30.0.55 | `ssh username@10.30.0.55` | `username` | `password` | https://10.30.0.55 |
| **HAPI FHIR** | 10.30.0.56 | `ssh username@10.30.0.56` | `username` | `password` | http://10.30.0.56:4180/fhir/ |
| **Keycloak** | 10.30.0.57 | `ssh username@10.30.0.57` | `username` | `password` | http://10.30.0.57:8080 |
| **HashiCorp Vault** | 10.30.0.58 | `ssh username@10.30.0.58` | `username` | `password` | http://10.30.0.58:8200 |
| **Elasticsearch** | 10.30.0.60 | `ssh username@10.30.0.60` | `username` | `password` | https://10.30.0.60:9200 |

### Raspberry Pi Devices

| Device | IP Address | SSH Command | Username | Password | Purpose |
|--------|------------|-------------|----------|----------|---------|
| **Pi #1** | 10.30.0.20 | `ssh username@10.30.0.20` | `username` | `password` | Heart Rate Monitor (72 BPM) |
| **Pi #2** | 10.30.0.21 | `ssh username@10.30.0.21` | `username` | `password` | Heart Rate Monitor (68 BPM) |
| **Pi #3** | 10.30.0.22 | `ssh username@10.30.0.22` | `username` | `password` | Heart Rate Monitor (75 BPM) |
| **Pi #4** | 10.30.0.23 | `ssh username@10.30.0.23` | `username` | `password` | Heart Rate Monitor (AFib) |
| **Pi #5** | 10.30.0.24 | `ssh username@10.30.0.24` | `username` | `password` | Heart Rate Monitor (70 BPM) |
| **Secure Pi** | 10.30.0.25 | `ssh username@10.30.0.25` | `username` | `password` | Balloon Demo - Secure System |
| **Vulnerable Pi** | 192.168.50.100 | `ssh username@192.168.50.100` | `username` | `password` | Balloon Demo - Vulnerable System |

### Web Interface Credentials

| Service | URL | Local Login | SSO Login (Keycloak) | Notes |
|---------|-----|-------------|----------------------|-------|
| **Node-RED** | http://10.30.0.52:1880 | N/A | `username` or `username` / `password` | SSO required |
| **Grafana** | http://10.30.0.53:3000 | `admin` / `password` | `username` or `username` / `password` | Both methods work |
| **Mirth Connect** | https://10.30.0.54:8443 | `admin` / `password` | N/A | Local only |
| **Wazuh** | https://10.30.0.55 | `admin` / `password` | ~~SSO broken~~ | **Use basic auth only** |
| **HAPI FHIR** | http://10.30.0.56:4180/fhir/ | N/A | `username` or `username` / `password` | SSO working, firewall blocks external access (port 4180) |
| **Keycloak Admin** | http://10.30.0.57:8080 | `admin` / `password` | N/A | Local only |
| **Vault** | http://10.30.0.58:8200 | Token: `password` | `username` or `username` / `password` | **Use Token for full admin access** (OIDC=limited) |
| **Elasticsearch** | https://10.30.0.60:9200 | `elastic` / `password` | N/A | API only |

### MQTT Credentials
- **Broker:** 10.30.0.51:1883
- **Username:** `username`
- **Password:** `password`
- **TLS:** Not enabled (plaintext on port 1883)

### Database Credentials
- **PostgreSQL Host:** 10.30.0.50:5432
- **Database:** `hospital_data`
- **Username:** `nodered`
- **Password:** `password`
- **SSL Mode:** `require` (self-signed certificate)

---

## 🚀 Cold Start Procedure (Powered-Down State)

### Phase 1: Physical Infrastructure (5 minutes)

1. **Power on TrueNAS Server**
   - Press power button on Dell PowerEdge server
   - Wait for POST (Power-On Self-Test) to complete
   - iDRAC should become accessible at http://10.30.0.45
   - **Wait 5 minutes** for TrueNAS to fully boot

2. **Verify Network Infrastructure**
   - UDM-SE gateway should auto-start (always on)
   - UniFi Switch Pro Max 24 PoE should auto-start (always on)
   - All devices should be reachable once TrueNAS is up

### Phase 2: Core Services Startup (10 minutes)

3. **Verify TrueNAS is Online**
   ```bash
   ping 10.30.0.44
   # Should respond
   ```
   - Web UI: http://10.30.0.44
   - Login: `username` / `password`

4. **Start Virtual Machines (Auto-Start Enabled)**
   - All VMs are configured to auto-start when TrueNAS boots
   - **Wait 10 minutes** for all VMs to boot
   - Expected boot order:
     1. PostgreSQL (10.30.0.50) - Foundation database
     2. MQTT Broker (10.30.0.51) - Messaging backbone
     3. Keycloak (10.30.0.57) - Identity provider
     4. Elasticsearch (10.30.0.60) - Log storage
     5. All other VMs in parallel

5. **Verify Core VMs are Up**
   ```bash
   # Ping all critical VMs
   ping 10.30.0.50  # PostgreSQL
   ping 10.30.0.51  # MQTT
   ping 10.30.0.57  # Keycloak
   ping 10.30.0.52  # Node-RED
   ping 10.30.0.53  # Grafana
   ```

### Phase 3: Critical Post-Boot Tasks (5 minutes)

6. **Unseal HashiCorp Vault (REQUIRED)**

   Vault requires manual unsealing after every restart. You need 3 of 5 keys.

   **Method 1: Web UI (RECOMMENDED - No CLI needed)**

   1. Open a web browser on your main computer
   2. Go to: **http://10.30.0.58:8200**
   3. You'll see "Unseal Vault" page with a text box
   4. Paste first key: `password`
   5. Click "Unseal" button
   6. Paste second key: `password`
   7. Click "Unseal" button
   8. Paste third key: `password`
   9. Click "Unseal" button - Vault is now unsealed!
   10. The page will redirect to the login screen (Vault is ready)

   **Method 2: Via CLI (Alternative - SSH to Vault VM)**

   ```bash
   # SSH to Vault VM (vault CLI is pre-installed there)
   ssh username@10.30.0.58

   # Run unseal commands
   export VAULT_ADDR='http://localhost:8200'
   vault operator unseal password
   vault operator unseal password
   vault operator unseal password

   # Verify unsealed
   vault status
   # Should show: Sealed: false
   ```

7. **Verify PostgreSQL Database is Running**
   ```bash
   ssh username@10.30.0.50

   # Check PostgreSQL service
   sudo systemctl status postgresql
   # Should show: active (exited)

   # Verify database connection
   sudo -u postgres psql -d hospital_data -c "SELECT COUNT(*) FROM heartrate_data;"
   # Should return current row count (~60M rows for 7 days)
   ```

8. **Check pg_cron Archival Job Status**
   ```bash
   # On PostgreSQL VM
   sudo -u postgres psql -d hospital_data -c "SELECT jobid, schedule, command, jobname, active FROM cron.job;"
   # Should show: daily-heartrate-archival job at 0 2 * * * (2 AM daily)

   # Check recent execution status
   sudo -u postgres psql -d hospital_data -c "SELECT jobid, status, return_message, start_time, end_time FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;"
   # Should show recent successful runs (status = 'succeeded')
   ```

### Phase 4: Raspberry Pi Devices (2 minutes)

9. **Power on Raspberry Pis**
   - Pi #1-4: Powered by PoE++ from switch (auto-start when switch is on)
   - Pi #5: External power adapter (plug in manually)
   - Secure Pi (10.30.0.25): External power adapter (plug in manually)
   - Vulnerable Pi (192.168.50.100): External power adapter (plug in manually)

   **Wait 2 minutes for Pis to boot**

10. **Verify Raspberry Pi Services**
    ```bash
    # Check each heart rate monitor Pi (1-5)
    ssh username@10.30.0.20
    sudo systemctl status heartrate1.service
    # Should show: active (running)
    # Repeat for Pi #2-5

    # Check balloon demo Pis
    ssh username@10.30.0.25
    sudo systemctl status balloon-control-api.service
    # Should show: active (running)

    ssh username@192.168.50.100
    sudo systemctl status balloon-control-api.service
    # Should show: active (running)
    ```

### Phase 5: Data Pipeline Verification (5 minutes)

11. **Verify MQTT Data Flow**
    ```bash
    # From any machine with mosquitto-clients
    mosquitto_sub -h 10.30.0.51 -u username -P password -t '#' -v
    # Should see messages from:
    # - hospital/heartrate/pi-{1,2,3,4,5}
    # - balloon/vulnerable/pressure
    # - balloon/vulnerable/relays
    # - balloon/secure/status
    ```

12. **Verify Node-RED Dashboard**
    - Open: http://10.30.0.52:1880/ui
    - Should see:
      - 5 heart rate gauges updating in real-time
      - 5 ECG waveform charts
      - Balloon demo gauges (upstream/downstream for both systems)
      - Security status panel (bottom right)

13. **Verify PostgreSQL Data Ingestion**
    ```bash
    ssh username@10.30.0.50

    # Check latest data timestamp
    sudo -u postgres psql -d hospital_data -c "SELECT MAX(timestamp), pi_id, bpm FROM heartrate_data GROUP BY pi_id ORDER BY pi_id;"
    # Should show recent timestamps (within last 5 seconds)
    ```

14. **Verify Grafana Dashboards**
    - Open: http://10.30.0.53:3000
    - Login with Keycloak SSO or local admin
    - Check dashboards:
      - Heart rate monitoring dashboard
      - IDS dashboard (if Suricata is running)

---

## ✅ Quick Health Check Checklist

Use this after startup to verify everything is operational:

### Infrastructure
- [ ] TrueNAS web UI accessible (http://10.30.0.44)
- [ ] All VMs showing "Running" in TrueNAS
- [ ] Network connectivity to all IPs (10.30.0.50-60)

### Core Services
- [ ] PostgreSQL responding to queries
- [ ] MQTT broker accepting connections (port 1883)
- [ ] Keycloak admin console accessible
- [ ] Vault unsealed and responding

### Data Pipeline
- [ ] All 5 Raspberry Pis publishing heartrate data
- [ ] Balloon demo Pis publishing pressure data
- [ ] Node-RED dashboard updating in real-time
- [ ] PostgreSQL receiving new rows (check MAX(timestamp))
- [ ] Mirth Connect channel "HeartRate_FHIR_Final" running
- [ ] HAPI FHIR receiving Observation resources

### Optional Services
- [ ] Grafana dashboards loading
- [ ] Wazuh agents reporting (14 agents total)
- [ ] Elasticsearch accepting connections

---

## 🔧 Common Troubleshooting

### Issue: Vault Shows "Sealed"

**Symptoms:** Vault web UI shows red "Sealed" status, cannot access secrets

**Solution:**
```bash
export VAULT_ADDR='http://10.30.0.58:8200'
vault operator unseal password
vault operator unseal password
vault operator unseal password
```

**Prevention:** This is normal behavior after power loss/restart. Always unseal manually.

---

### Issue: HAPI FHIR Docker Container Not Running

**Symptoms:** HAPI FHIR web UI not accessible, Mirth cannot send data

**Solution:**
```bash
ssh username@10.30.0.56

# Check Docker container status
sudo docker ps -a | grep hapi-fhir

# If container is stopped, start it
sudo docker start hapi-fhir

# If container doesn't exist, recreate it
sudo docker run -d --name hapi-fhir \
  --restart always \
  -p 8080:8080 \
  -e spring.datasource.url='jdbc:postgresql://10.30.0.50:5432/hapi_fhir?ssl=true&sslmode=require' \
  -e spring.datasource.username='nodered' \
  -e spring.datasource.password='password' \
  -e spring.datasource.driverClassName='org.postgresql.Driver' \
  -e hapi.fhir.allow_external_references=true \
  -e JAVA_OPTS='-Xms512m -Xmx3072m' \
  hapiproject/hapi:latest

# Verify container is running
sudo docker logs hapi-fhir
```

---

### Issue: Node-RED Shows "No Data" on Dashboard

**Symptoms:** Gauges show 0 or "No data", charts empty

**Solution:**
```bash
# Step 1: Check MQTT broker is accessible
mosquitto_sub -h 10.30.0.51 -u username -P password -t '#' -v
# Should see messages flowing

# If no messages:
# Step 2: Check Raspberry Pis are publishing
ssh username@10.30.0.20
sudo journalctl -u heartrate1.service -n 50
# Should show MQTT publish attempts

# If publishing but Node-RED not receiving:
# Step 3: Restart Node-RED service
ssh username@10.30.0.52
sudo systemctl restart nodered.service

# Step 4: Check Node-RED logs
sudo journalctl -u nodered.service -f
# Look for MQTT connection messages
```

---

### Issue: Raspberry Pi Service Not Running

**Symptoms:** Heartrate monitor not publishing, balloon demo not responding

**Solution:**
```bash
# SSH to the affected Pi
ssh username@10.30.0.20  # (or whichever Pi)

# Check service status
sudo systemctl status heartrate1.service

# If failed, check logs
sudo journalctl -u heartrate1.service -n 50

# Restart service
sudo systemctl restart heartrate1.service

# If still failing, check MQTT connectivity
mosquitto_pub -h 10.30.0.51 -u username -P password -t 'test/topic' -m 'test'
# Should succeed with no errors
```

---

### Issue: PostgreSQL Not Accepting Connections

**Symptoms:** Node-RED shows database errors, HAPI FHIR can't connect

**Solution:**
```bash
ssh username@10.30.0.50

# Check PostgreSQL service
sudo systemctl status postgresql
# If not active, start it
sudo systemctl start postgresql

# Verify listening on port 5432
sudo ss -tlnp | grep 5432
# Should show postgres listening

# Check recent logs
sudo tail -100 /var/log/postgresql/postgresql-16-main.log

# Test local connection
sudo -u postgres psql -d hospital_data -c "SELECT 1;"
# Should return 1
```

---

### Issue: Grafana Dashboards Not Loading

**Symptoms:** Grafana UI loads but panels show errors or no data

**Solution:**
```bash
ssh username@10.30.0.53

# Check Grafana service
sudo systemctl status grafana-server

# Verify PostgreSQL data source
# Go to Grafana UI → Configuration → Data Sources → PostgreSQL
# Click "Test" button, should show "Database Connection OK"

# If SSL error, update data source:
sudo sqlite3 /var/lib/grafana/grafana.db "UPDATE data_source SET json_data = json_set(json_data, '$.sslmode', 'require') WHERE type = 'grafana-postgresql-datasource';"

# Restart Grafana
sudo systemctl restart grafana-server
```

---

### Issue: pg_cron Archival Not Running

**Symptoms:** Active heartrate_data table has more than 7-8 days of data

**Solution:**
```bash
ssh username@10.30.0.50

# Check cron job configuration
sudo -u postgres psql -d hospital_data -c "SELECT jobid, schedule, command, jobname, active FROM cron.job;"
# Should show daily-heartrate-archival job

# Check recent execution status
sudo -u postgres psql -d hospital_data -c "SELECT jobid, status, return_message, start_time, end_time FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;"

# If showing "connection failed":
# Verify cron.database_name is set
sudo -u postgres psql -d hospital_data -c "SHOW cron.database_name;"
# Should return: hospital_data

# If not set, edit postgresql.conf
sudo nano /etc/postgresql/16/main/postgresql.conf
# Add: cron.database_name = 'hospital_data'
# Restart PostgreSQL
sudo systemctl restart postgresql

# Manually run archival to catch up
sudo -u postgres psql -d hospital_data -c "SELECT archive_old_heartrate_data();"
```

---

### Issue: Balloon Demo Pis Not Responding

**Symptoms:** Pressure gauges on Node-RED dashboard not updating

**Solution:**
```bash
# Check vulnerable Pi
ssh username@192.168.50.100
sudo systemctl status balloon-control-api.service
sudo journalctl -u balloon-control-api.service -n 50

# Check secure Pi
ssh username@10.30.0.25
sudo systemctl status balloon-control-api.service
sudo journalctl -u balloon-control-api.service -n 50

# Verify MQTT publishing
mosquitto_sub -h 10.30.0.51 -u username -P password -t 'balloon/#' -v
# Should see balloon/vulnerable/* and balloon/secure/* topics

# Restart services if needed
sudo systemctl restart balloon-control-api.service
```

---

### Issue: HAPI FHIR OAuth2 Proxy High Restart Count

**Symptoms:** OAuth2 Proxy shows very high restart counter (100k+ restarts), but currently running

**Status:** Not a critical issue - service is functional once running

**Cause:** OAuth2 Proxy tries to start before Keycloak is ready during VM boot sequence, causing repeated restart attempts. Once Keycloak is available, OAuth2 Proxy runs successfully.

**Verification:**
```bash
ssh username@10.30.0.56
sudo systemctl status oauth2-proxy
# Should show "active (running)" despite high restart count
```

**Note:** High restart counter is cumulative over months of operation. Current instance runs stable once Keycloak is available.

---

### Issue: Keycloak SSO Not Working (Wazuh Specific)

**Symptoms:** Wazuh SSO fails with "Unauthorized" error after Keycloak login, dashboard shows "Wazuh did not load properly"

**Status:** **KNOWN ISSUE - SSO disabled as of 2026-03-24**

**Current Workaround:** Use basic authentication instead
- URL: https://10.30.0.55
- Username: `admin`
- Password: `password`

**Root Cause:** OpenSearch backend SSL configuration was altered during SSO setup attempt. Running `securityadmin.sh` changed SSL client certificate requirements, breaking the connection between dashboard and backend. No backup of working configuration available.

**For Details:** See `TROUBLESHOOTING_HISTORY.md` entry "Wazuh SIEM Keycloak SSO Broken After securityadmin.sh (2026-03-24)" for complete investigation timeline and attempted fixes.

**Note:** Keycloak itself is working fine - Node-RED, Grafana, HAPI FHIR, and Vault SSO all functional. Only Wazuh SSO is affected.

---

### Issue: Mirth Connect Channel Stopped

**Symptoms:** HAPI FHIR not receiving new Observations, Mirth shows channel stopped

**Solution:**
```bash
# Via web UI (easier):
# Open: https://10.30.0.54:8443
# Login: admin / password
# Right-click "HeartRate_FHIR_Final" channel → Start

# Via SSH:
ssh username@10.30.0.54
sudo systemctl status mirthconnect

# Check Mirth logs
sudo tail -100 /opt/mirthconnect/logs/mirth.log

# Restart Mirth if needed
sudo systemctl restart mirthconnect
```

---

### Issue: Wazuh Agents Not Reporting

**Symptoms:** Wazuh dashboard shows agents as "Disconnected"

**Solution:**
```bash
# On Wazuh SIEM server
ssh username@10.30.0.55

# Check Wazuh manager status
sudo systemctl status wazuh-manager

# List agent status
sudo /var/ossec/bin/agent_control -l
# Should show 14 agents, all "Active"

# If agents disconnected, restart Wazuh manager
sudo systemctl restart wazuh-manager

# On individual agent (if specific agent is down)
ssh <agent-machine>
sudo systemctl status wazuh-agent
sudo systemctl restart wazuh-agent
```

---

## 📊 System Status Dashboard

### Expected Data Volumes (as of 2026-03-23)

**PostgreSQL:**
- **Active Table:** ~60M rows (last 7 days, ~8.6M rows/day)
- **Archive Table:** ~865M rows (historical data >7 days old)
- **Total Database Size:** ~140 GB (active + archive + indexes)
- **Daily Growth:** ~8.6M rows/day (~1.2 GB/day)

**MQTT Message Rates:**
- Pi #1-5 (heartrate): 1 msg/sec each = 5 msg/sec total
- Vulnerable Pi: 10 msg/sec (balloon data)
- Secure Pi: ~2 msg/sec (balloon data)
- **Total:** ~17 msg/sec continuous

**HAPI FHIR:**
- Ingestion rate: 1 Observation/sec (rate-limited via Mirth)
- Database: ~35 GB (hapi_fhir PostgreSQL database)

---

## 🔑 Critical Vault Unseal Keys (Keep Secure!)

**Root Token:** `password`

**Unseal Keys (Need 3 of 5):**
1. `password`
2. `password`
3. `password`
4. `password`
5. `password`

---

## 📞 Emergency Contacts

- **TrueNAS iDRAC (Physical Server Management):** http://10.30.0.45
- **Network Gateway (UDM-SE):** https://10.30.0.1 (username / password)

---

## 📚 Related Documentation

- `CLAUDE.md` - Complete project overview and architecture
- `NETWORK_SETUP_PROGRESS_PART1.md` - Detailed network configuration
- `TROUBLESHOOTING_HISTORY.md` - Historical troubleshooting solutions
- `SECURITY_HARDENING_2026-02-13.md` - Security configuration details
- `VM_SERVICES_STATUS.md` - Current status of all VMs

---

**Last Verified:** 2026-03-23
**Total Startup Time:** ~20-25 minutes from powered-down state
