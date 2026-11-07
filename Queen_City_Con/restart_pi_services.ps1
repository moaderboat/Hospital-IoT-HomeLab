# Resync clocks, then restart the hospital Pi services (needed after each cold boot) plus Filebeat.
# Run AFTER the VMs are up (MQTT VM 10.30.0.51 is also the NTP server). From the desktop (has SSH keys):
#
#   powershell -ExecutionPolicy Bypass -File .\restart_pi_services.ps1
#       -> hospital Pis #1-#5 + Filebeat ONLY. Does NOT touch the pressure demo boards.
#
#   powershell -ExecutionPolicy Bypass -File .\restart_pi_services.ps1 -IncludeDemoBoards
#       -> ALSO restarts the Secure + Vulnerable Pi control services.
#          !! This STARTS the PUMPS AND VALVES (they pressurize the bottles to 25 PSI) !!
#          You must type YES to confirm. Do it only with bottles fitted, the area clear and the kill switch in reach.
#
# Why the clock step: the Pis have no RTC. After a power cut they boot with an old time, and if the
# NTP server (10.30.0.51) wasn't up yet, timesyncd gives up. Their readings are then timestamped hours
# in the past and Grafana shows "No data" (found 2026-11-06).

param([switch]$IncludeDemoBoards)

$targets = @(
    @{ Host = 'username@10.30.0.20';    Services = @('heartrate1') },
    @{ Host = 'username@10.30.0.21';    Services = @('heartrate2') },
    @{ Host = 'username@10.30.0.22';    Services = @('heartrate3') },
    @{ Host = 'username@10.30.0.23';    Services = @('heartrate4') },
    @{ Host = 'username@10.30.0.24';    Services = @('heartrate5') },
    @{ Host = 'username@192.168.50.191'; Services = @('filebeat') }
)

if ($IncludeDemoBoards) {
    Write-Host ''
    Write-Host '!! WARNING: this will START THE PUMPS AND VALVES on both pressure demo boards. !!' -ForegroundColor Red
    Write-Host '   Bottles fitted? Area clear? Kill switch within reach?' -ForegroundColor Red
    $answer = Read-Host 'Type YES to include the demo boards (anything else = hospital Pis only)'
    if ($answer -ceq 'YES') {
        $targets += @{ Host = 'username@10.30.0.25';     Services = @('balloon-control-secure') }
        $targets += @{ Host = 'username@192.168.50.100'; Services = @('balloon-sensor-publisher', 'balloon-control-api') }
    } else {
        Write-Host 'Demo boards skipped.' -ForegroundColor Yellow
    }
}

# No double quotes in here on purpose: Windows PowerShell 5.1 strips them when passing arguments to ssh.
$remote = @'
sudo systemctl restart systemd-timesyncd
for i in $(seq 1 15); do [ $(timedatectl show -p NTPSynchronized --value) = yes ] && break; sleep 2; done
echo -n '   clock: '; date '+%F %T'; echo -n '   synced='; timedatectl show -p NTPSynchronized --value
sudo systemctl restart __SVC__ && echo -n '   services: ' && systemctl is-active __SVC__ | tr '\n' ' '; echo
'@

$pcNow = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Write-Host "This computer's time: $pcNow (each clock below should be within a few seconds)" -ForegroundColor Yellow
foreach ($t in $targets) {
    $svc = $t.Services -join ' '
    Write-Host "== $($t.Host): resync clock, restart $svc" -ForegroundColor Cyan
    $cmd = $remote.Replace('__SVC__', $svc) -replace "`r", ''
    ssh -t -o ConnectTimeout=5 $t.Host $cmd
    if ($LASTEXITCODE -ne 0) { Write-Host "   FAILED on $($t.Host) - see field guide section 8" -ForegroundColor Red }
}
Write-Host ''
Write-Host 'Done. Any "synced=no" or a clock that is off: check chrony on 10.30.0.51 (ssh username@10.30.0.51 "chronyc tracking; chronyc clients").' -ForegroundColor Yellow
Write-Host 'Then run .\con_health_check.ps1 and look at Grafana (data should appear within a minute).' -ForegroundColor Green
