# Network Configuration Instructions for SPOTLAWFUL AI LAN Deployment

## 1. Server Network Setup

Assign a static IP address to the server machine or configure a DHCP reservation in your router to ensure the server IP does not change.

Verify the server is connected to the LAN and can be pinged from client devices.

## 2. Firewall Configuration

Open Windows Defender Firewall with Advanced Security.

Create a new inbound rule:

- Rule Type: Port

- Protocol: TCP

- Port Number: 5000

- Action: Allow the connection

- Profile: Private (and Public if needed)

- Name: Allow SPOTLAWFUL AI API Server Port 5000

Ensure no other security software blocks inbound connections on port 5000.
