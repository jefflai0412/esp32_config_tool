import subprocess
import time

network_name = "None"

# Command to connect to Wi-Fi network
ssid = "Yallvend_Office"
command = f'netsh wlan connect name="{ssid}" ssid="{ssid}" interface="Wi-Fi"'
try:
    # Execute the command
    subprocess.call(command, shell=True)
except Exception as e:
    print(e)

# Wait for a brief moment to allow the connection to establish
time.sleep(2)

# Run the netsh command to get the current Wi-Fi network name
result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
output = result.stdout
print(output)
# Extract the network name from the output
for line in output.splitlines():
    if "SSID" in line:
        network_name = line.split(":")[1].strip()
        print(network_name)
        break

print("Connected to:", network_name)
