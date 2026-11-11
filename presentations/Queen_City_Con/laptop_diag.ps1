# Read-only network diagnostics for the admin laptop. Changes nothing.
# Run: right-click this file -> "Run with PowerShell"
#   or: powershell -ExecutionPolicy Bypass -File .\laptop_diag.ps1
# Results are saved next to this script as laptop_diag_output.txt (synced by OneDrive).

$out = Join-Path $PSScriptRoot 'laptop_diag_output.txt'
$lines = New-Object System.Collections.Generic.List[string]
function Add([string]$s) { $lines.Add($s); Write-Host $s }

Add "=== laptop_diag $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') on $env:COMPUTERNAME"

Add "`n=== Adapters that are up"
Get-NetIPConfiguration | Where-Object { $_.NetAdapter.Status -eq 'Up' } | ForEach-Object {
    Add ("{0} | IPv4 {1} | GW {2} | DNS {3} | MAC {4} | DHCP {5}" -f $_.InterfaceAlias,
        ($_.IPv4Address.IPAddress -join ','), ($_.IPv4DefaultGateway.NextHop -join ','),
        ($_.DNSServer.ServerAddresses -join ','), $_.NetAdapter.MacAddress,
        (Get-NetIPInterface -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4).Dhcp)
}

function Test-Port([string]$Ip, [int]$Port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($Ip, $Port, $null, $null); return ($a.AsyncWaitHandle.WaitOne(2000) -and $c.Connected) }
    catch { return $false } finally { $c.Close() }
}

Add "`n=== Reachability"
$targets = @(
    @('UDM-SE (VLAN30)', '10.30.0.1', 443),
    @('UDM-SE (Default)', '192.168.0.1', 443),
    @('Switch mgmt', '192.168.0.130', 443),
    @('TrueNAS', '10.30.0.44', 80),
    @('Node-RED', '10.30.0.52', 1880),
    @('Vulnerable Pi', '192.168.50.100', 22)
)
$ping = New-Object System.Net.NetworkInformation.Ping
foreach ($t in $targets) {
    $p = $false; try { $p = ($ping.Send($t[1], 1000).Status -eq 'Success') } catch {}
    Add ("{0,-18} {1,-15} ping={2,-5} tcp{3}={4}" -f $t[0], $t[1], $p, $t[2], (Test-Port $t[1] $t[2]))
}

Add "`n=== ARP table (who answered on the wire)"
arp -a | ForEach-Object { Add $_ }

Add "`n=== Routes (IPv4)"
route print -4 | Select-String '^\s+\d' | ForEach-Object { Add $_.Line }

$lines | Set-Content -Path $out -Encoding UTF8
Write-Host "`nSaved to $out" -ForegroundColor Green
Read-Host 'Press Enter to close'
