# PowerShell script to diagnose network connectivity issues to the SPOTLAWFUL AI API server

$serverIp = "192.168.0.103"
$port = 5000

Write-Output "Pinging server $serverIp..."
Test-Connection -ComputerName $serverIp -Count 4

Write-Output "Testing TCP port $port on $serverIp..."
$tcpTest = Test-NetConnection -ComputerName $serverIp -Port $port

if ($tcpTest.TcpTestSucceeded) {
    Write-Output "TCP port $port is open on $serverIp."
} else {
    Write-Output "TCP port $port is NOT open on $serverIp."
}

Write-Output "Checking local firewall rules for port $port..."
Get-NetFirewallRule | Where-Object {
    $_.Direction -eq 'Inbound' -and $_.Enabled -eq 'True'
} | ForEach-Object {
    $rule = $_
    $ports = (Get-NetFirewallPortFilter -AssociatedNetFirewallRule $rule).LocalPort
    if ($ports -contains $port) {
        Write-Output "Firewall rule '$($rule.DisplayName)' allows port $port."
    }
}

Write-Output "Please run this script on client machines to verify connectivity."
