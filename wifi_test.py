import subprocess

# Run the netsh command to get the current Wi-Fi network name
result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
print(result)
output = result.stdout

# Extract the network name from the output
for line in output.splitlines():
    if "SSID" in line:
        network_name = line.split(":")[1].strip()
        break

# print("Connected to:", network_name)