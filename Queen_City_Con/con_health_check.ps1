# Queen City Con lab health check. Run from the admin laptop (on VLAN 30):
#   powershell -ExecutionPolicy Bypass -File .\con_health_check.ps1
# Pings every device and tests every service port. Read-only: changes nothing.
# Note: run from the home desktop (via the UDM-SE WAN), the UDM-SE itself (10.30.0.1) shows red. That's normal.
# From the admin laptop on UDM-SE port 1 it should be green.

$checks = @(
    @{ Name = 'UDM-SE gateway';        Ip = '10.30.0.1';      Ports = @(443) },
    @{ Name = 'Switch (mgmt)';         Ip = '192.168.0.130';  Ports = @() },
    @{ Name = 'TrueNAS';               Ip = '10.30.0.44';     Ports = @(80) },
    @{ Name = 'iDRAC';                 Ip = '10.30.0.45';     Ports = @(443) },
    @{ Name = 'PostgreSQL';            Ip = '10.30.0.50';     Ports = @(5432) },
    @{ Name = 'MQTT + NTP';            Ip = '10.30.0.51';     Ports = @(1883) },
    @{ Name = 'Node-RED';              Ip = '10.30.0.52';     Ports = @(1880) },
    @{ Name = 'Grafana';               Ip = '10.30.0.53';     Ports = @(3000) },
    @{ Name = 'Mirth Connect';         Ip = '10.30.0.54';     Ports = @(8443, 8081) },
    @{ Name = 'Wazuh';                 Ip = '10.30.0.55';     Ports = @(443) },
    @{ Name = 'HAPI FHIR (proxy)';     Ip = '10.30.0.56';     Ports = @(4180) },
    @{ Name = 'Keycloak';              Ip = '10.30.0.57';     Ports = @(8080) },
    @{ Name = 'Vault';                 Ip = '10.30.0.58';     Ports = @(8200) },
    @{ Name = 'Elasticsearch';         Ip = '10.30.0.60';     Ports = @(9200) },
    @{ Name = 'Pi #1';                 Ip = '10.30.0.20';     Ports = @(22) },
    @{ Name = 'Pi #2';                 Ip = '10.30.0.21';     Ports = @(22) },
    @{ Name = 'Pi #3';                 Ip = '10.30.0.22';     Ports = @(22) },
    @{ Name = 'Pi #4';                 Ip = '10.30.0.23';     Ports = @(22) },
    @{ Name = 'Pi #5';                 Ip = '10.30.0.24';     Ports = @(22) },
    @{ Name = 'Secure Pi';             Ip = '10.30.0.25';     Ports = @(22, 5000) },
    @{ Name = 'Vulnerable Pi';         Ip = '192.168.50.100'; Ports = @(22, 5000) },
    @{ Name = 'Suricata laptop';       Ip = '192.168.50.191'; Ports = @(22) }
)

function Test-Port([string]$Ip, [int]$Port, [int]$TimeoutMs = 1500) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($Ip, $Port, $null, $null)
        if ($async.AsyncWaitHandle.WaitOne($TimeoutMs) -and $client.Connected) { return $true }
        return $false
    } catch { return $false } finally { $client.Close() }
}

$ping = New-Object System.Net.NetworkInformation.Ping
$bad = 0
Write-Host ("{0,-20} {1,-16} {2,-6} {3}" -f 'Device', 'IP', 'Ping', 'Ports') -ForegroundColor Cyan
foreach ($c in $checks) {
    $pingOk = $false
    try { $pingOk = ($ping.Send($c.Ip, 1000).Status -eq 'Success') } catch {}
    $portText = @()
    $allPortsOk = $true
    foreach ($p in $c.Ports) {
        $ok = Test-Port $c.Ip $p
        if (-not $ok) { $allPortsOk = $false }
        $portText += ('{0}:{1}' -f $p, $(if ($ok) { 'ok' } else { 'DOWN' }))
    }
    # Some hosts (e.g. the UDM-SE) may not answer ping; treat open ports as reachable.
    $reachable = $pingOk -or ($c.Ports.Count -gt 0 -and $allPortsOk)
    $good = $reachable -and $allPortsOk
    if (-not $good) { $bad++ }
    $line = "{0,-20} {1,-16} {2,-6} {3}" -f $c.Name, $c.Ip, $(if ($pingOk) { 'ok' } else { 'no' }), ($portText -join '  ')
    Write-Host $line -ForegroundColor $(if ($good) { 'Green' } else { 'Red' })
}

Write-Host ''
if ($bad -eq 0) {
    Write-Host 'ALL GREEN. Now check Vault is unsealed and the dashboards show live data (field guide section 5).' -ForegroundColor Green
} else {
    Write-Host "$bad item(s) RED. VMs can take ~15 min after power-on. VLAN 2 reds usually mean the Mock WAN or firewall rules (field guide section 8)." -ForegroundColor Yellow
}
