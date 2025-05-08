# PowerShell script to add Windows Firewall rule to allow inbound TCP traffic on port 5000

$ruleName = "Allow SPOTLAWFUL AI API Server Port 5000"
$port = 5000

# Check if the rule already exists
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($null -eq $existingRule) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Profile Private
    Write-Output "Firewall rule '$ruleName' created to allow inbound TCP traffic on port $port."
} else {
    Write-Output "Firewall rule '$ruleName' already exists."
}
