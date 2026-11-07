#!/bin/bash
# Deployment script for HeartRate monitor MQTT updates
# Run this script from your WSL/Linux environment

set -e  # Exit on error

PASSWORD="password"
SCRIPT_DIR="hospital scripts/heartrate"
REMOTE_DIR="Desktop/hospital-scripts/heartrate"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}HeartRate Monitor MQTT Update Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Array of Pi configurations: "pi_number:ip_address:script_name"
PIS=(
    "1:10.30.0.20:HeartRate1Monitor.py"
    "2:10.30.0.21:HeartRate2Monitor.py"
    "3:10.30.0.22:HeartRate3Monitor.py"
    "4:10.30.0.23:HeartRate4Monitor.py"
    "5:10.30.0.24:HeartRate5Monitor.py"
)

# Function to run SSH command with password
run_ssh() {
    local user=$1
    local host=$2
    local cmd=$3
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "${user}@${host}" "$cmd"
}

# Function to copy file with password
run_scp() {
    local src=$1
    local user=$2
    local host=$3
    local dest=$4
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$src" "${user}@${host}:${dest}"
}

# Step 1: Install paho-mqtt on all Pis
echo -e "${YELLOW}Step 1: Installing paho-mqtt on all Raspberry Pis...${NC}"
for pi_config in "${PIS[@]}"; do
    IFS=':' read -r pi_num ip script <<< "$pi_config"
    echo -e "  Installing on Pi #${pi_num} (${ip})..."
    run_ssh "r-pi-${pi_num}" "$ip" "sudo pip3 install paho-mqtt --break-system-packages" || echo -e "${RED}    Warning: Install may have failed${NC}"
done
echo -e "${GREEN}✓ paho-mqtt installation complete${NC}"
echo ""

# Step 2: Deploy updated scripts
echo -e "${YELLOW}Step 2: Deploying updated scripts...${NC}"
for pi_config in "${PIS[@]}"; do
    IFS=':' read -r pi_num ip script <<< "$pi_config"
    echo -e "  Deploying ${script} to Pi #${pi_num} (${ip})..."
    run_scp "${SCRIPT_DIR}/${script}" "r-pi-${pi_num}" "$ip" "${REMOTE_DIR}/${script}"
done
echo -e "${GREEN}✓ Script deployment complete${NC}"
echo ""

# Step 3: Restart systemd services
echo -e "${YELLOW}Step 3: Restarting systemd services...${NC}"
for pi_config in "${PIS[@]}"; do
    IFS=':' read -r pi_num ip script <<< "$pi_config"
    service_name="heartrate${pi_num}.service"
    echo -e "  Restarting ${service_name} on Pi #${pi_num}..."
    run_ssh "r-pi-${pi_num}" "$ip" "sudo systemctl restart ${service_name}"
    sleep 2
    # Check status
    status=$(run_ssh "r-pi-${pi_num}" "$ip" "sudo systemctl is-active ${service_name}")
    if [ "$status" == "active" ]; then
        echo -e "    ${GREEN}✓ Service is active${NC}"
    else
        echo -e "    ${RED}✗ Service failed to start${NC}"
    fi
done
echo -e "${GREEN}✓ Service restart complete${NC}"
echo ""

# Step 4: Test MQTT connection
echo -e "${YELLOW}Step 4: Testing MQTT messages...${NC}"
echo -e "  Subscribing to hospital/heartrate/# for 10 seconds..."
timeout 10 mosquitto_sub -h 10.30.0.51 -t "hospital/heartrate/#" -v || echo -e "${YELLOW}  (Timeout - check if messages appeared above)${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "All 5 Raspberry Pis should now be publishing heart rate data via MQTT."
echo -e "Monitor messages with: ${YELLOW}mosquitto_sub -h 10.30.0.51 -t 'hospital/heartrate/#' -v${NC}"
