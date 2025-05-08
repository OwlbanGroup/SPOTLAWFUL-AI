# 3. API Server Configuration

- Verify the API server is configured to listen on all interfaces (0.0.0.0) on port 5000 using the Waitress server.

- Confirm the server is running and listening on the correct port.

## 4. Router and Network Policies

- Verify LAN routing allows traffic between client devices and the server.

- If VLANs or subnet segmentation are used, ensure routing and firewall rules permit access.

## 5. Client Access

- Clients should access the API using the server’s LAN IP and port 5000.

- Test connectivity using curl, Postman, or a browser.

## 6. Monitoring and Maintenance

- Monitor server uptime and network performance.

- Regularly review firewall and network policies.

## Troubleshooting Tips

- Use `ping <server_ip>` to check basic connectivity.

- Use `telnet <server_ip> 5000` or `Test-NetConnection -ComputerName <server_ip> -Port 5000` in PowerShell to test port accessibility.

- Check Windows Event Logs for firewall or network errors.

If you need scripts or further assistance with any step, please ask.
