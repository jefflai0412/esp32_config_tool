import subprocess
import re


def connect_to_wifi(ssid):
    # Command to connect to Wi-Fi network
    command = f'netsh wlan connect name="{ssid}" ssid="{ssid}" interface="Wi-Fi"'
    # Execute the command
    subprocess.call(command, shell=True)


def scan_wifi_networks():
    # Command to scan Wi-Fi networks
    command = "netsh wlan show networks mode=Bssid"

    # Execute the command and capture the output
    result = subprocess.check_output(command, shell=True).decode()

    # Use regular expression to extract SSID names
    ssids = re.findall(r'SSID\s\d+\s:\s(\S+)', result)

    # Print the extracted SSIDs
    return ssids


# Usage
wifi_ssid = "C21H26O2"
connect_to_wifi(wifi_ssid)

# Usage
wifi_networks = scan_wifi_networks()
print(wifi_networks)