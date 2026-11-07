# Temporarily gives the laptop's wired adapter a lab IP, tests the UDM-SE, then puts the adapter back to DHCP.
# Needs ADMIN: open PowerShell as Administrator, cd to this folder, then:
#   powershell -ExecutionPolicy Bypass -File .\laptop_static_test.ps1
# Results go to laptop_static_test_output.txt next to this script.

$Alias = 'Ethernet'   # the Intel I219-LM wired port (from laptop_diag_output.txt)
$out = Join-Path $PSScriptRoot 'laptop_static_test_output.txt'
$log = New-Object System.Collections.Generic.List[string]
function Add([string]$s) { $log.Add($s); Write-Host $s }

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Run this from an ADMINISTRATOR PowerShell window.' -ForegroundColor Red; Read-Host 'Enter to close'; exit 1
}

function Test-Port([string]$Ip, [int]$Port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($Ip, $Port, $null, $null); return ($a.AsyncWaitHandle.WaitOne(2000) -and $c.Connected) }
    catch { return $false } finally { $c.Close() }
}

$plans = @(
    @{ Label = 'VLAN 30';         Ip = '10.30.0.30';   Targets = @(@('10.30.0.1',443), @('10.30.0.44',80), @('10.30.0.52',1880), @('10.30.0.51',1883)) },
    @{ Label = 'Default network'; Ip = '192.168.0.30'; Targets = @(@('192.168.0.1',443), @('192.168.0.130',443)) }
)

Add "=== laptop_static_test $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add ("Link: " + (Get-NetAdapter -Name $Alias | ForEach-Object { "$($_.Status) $($_.LinkSpeed)" }))

try {
    Set-NetIPInterface -InterfaceAlias $Alias -Dhcp Disabled -ErrorAction Stop
    foreach ($p in $plans) {
        Get-NetIPAddress -InterfaceAlias $Alias -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
        New-NetIPAddress -InterfaceAlias $Alias -IPAddress $p.Ip -PrefixLength 24 -ErrorAction Stop | Out-Null
        Start-Sleep 4
        $state = (Get-NetIPAddress -InterfaceAlias $Alias -IPAddress $p.Ip).AddressState
        Add "`n--- $($p.Label): laptop = $($p.Ip)/24 (address state: $state)"
        foreach ($t in $p.Targets) {
            $ping = Test-Connection $t[0] -Count 2 -Quiet
            Add ("{0,-15} ping={1,-5} tcp{2}={3}" -f $t[0], $ping, $t[1], (Test-Port $t[0] $t[1]))
        }
        Add 'ARP on the wired port:'
        arp -a -N $p.Ip | Select-String 'dynamic' | ForEach-Object { Add "  $($_.Line.Trim())" }
    }
}
catch { Add "ERROR: $($_.Exception.Message)" }
finally {
    Get-NetIPAddress -InterfaceAlias $Alias -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
    Set-NetIPInterface -InterfaceAlias $Alias -Dhcp Enabled
    Add "`nAdapter '$Alias' set back to DHCP."
    $log | Set-Content -Path $out -Encoding UTF8
    Write-Host "Saved to $out" -ForegroundColor Green
    Read-Host 'Press Enter to close'
}
