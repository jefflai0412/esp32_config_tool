import re
import subprocess
from tkinter import filedialog
import customtkinter as ctk
import requests
# ========================================== settings ==============================================
version = 3.0


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.geometry("700x600")
root.title("esp32 config")
font = ("Roboto", 14)
button_width = 100
button_height = 30
padx = 20
pady = 15


# ================================== frequently used function =======================================
def delete_all():
    response_frame.delete("0.0", '10000.10000')
    setSN_entry.delete('0', '100')
    setVidCode_entry.delete('0', '100')
    setDpsCode_entry.delete('0', '100')


# ==================================================================================================
# ======================================== create tabview ==========================================
# ==================================================================================================
tabview = ctk.CTkTabview(root, width=300, height=450)
tabview.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
tabview.add("WIFI")
tabview.add("factory")
tabview.add("setdb")

tabview.tab("WIFI").grid_columnconfigure(0, weight=1)
tabview.tab("factory").grid_columnconfigure(0, weight=1)
tabview.tab("setdb").grid_columnconfigure(0, weight=1)

# ==================================================================================================
# ========================================= mode switch ============================================
# ==================================================================================================
on_off = "OFF"


# ========================================= callbacks ==============================================
def mode_switch_calalback():
    global on_off
    if on_off == "OFF":
        on_off = "ON"
    else:
        on_off = "OFF"
    mode_switch.configure(text=f"工程模式:{on_off}")


# ========================================= elements ================================================
mode_switch = ctk.CTkSwitch(master=root, text=f"工程模式:{on_off}", height=button_height, command=mode_switch_calalback)
mode_switch.grid(row=0, column=1, padx=(20, 10), pady=20, sticky="nw")

# ==================================================================================================
# ===================================== create response frame ======================================
# ==================================================================================================
response_frame = ctk.CTkTextbox(master=root, width=300, height=400)
response_frame.grid(row=0, column=1, padx=(20, 10), pady=20, sticky="sew")

# ==================================================================================================
# =========================================== WIFI =================================================
# ==================================================================================================
ssids = []


# ========================================= callbacks ==============================================
def scan_button_callback():
    result = "None"
    connect_button.configure(text="連接")
    delete_all()
    global ssids
    # Command to scan Wi-Fi networks
    command = "netsh wlan show networks mode=Bssid"

    # Execute the command and capture the output
    try:
        result = subprocess.check_output(command, shell=True).decode()
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!!")

    # Use regular expression to extract SSID names
    ssids = re.findall(r'SSID\s\d+\s:\s(\S+)', result)
    WIFI_menu.configure(values=ssids)


def connect_button_callback():
    network_name = "None"
    # Run the netsh command to turn on Wi-Fi
    subprocess.run(["netsh", "interface", "set", "interface", "name='Wi-Fi'", "admin=enable"])
    # Command to connect to Wi-Fi network
    ssid = WIFI_menu.get()
    command = f'netsh wlan connect name="{ssid}" ssid="{ssid}" interface="Wi-Fi"'
    try:
        # Execute the command
        subprocess.call(command, shell=True)
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!!")
    # Run the netsh command to get the current Wi-Fi network name
    result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
    output = result.stdout
    # Extract the network name from the output
    for line in output.splitlines():
        if "SSID" in line:
            network_name = line.split(":")[1].strip()
            break
    response_frame.insert('0.0', f'已連接至:{network_name}')


# ========================================= elements ================================================
scan_button = ctk.CTkButton(tabview.tab("WIFI"), text='掃描WiFi', width=button_width, height=button_height,
                            command=scan_button_callback, font=font)
scan_button.grid(row=0, column=0, padx=20, pady=20)

WIFI_menu = ctk.CTkOptionMenu(tabview.tab("WIFI"), values=["選擇WiFi"], width=button_width, height=button_height)
WIFI_menu.grid(row=1, column=0, padx=20, pady=20)

connect_button = ctk.CTkButton(tabview.tab("WIFI"), text='連接', width=button_width, height=button_height,
                               command=connect_button_callback)
connect_button.grid(row=2, column=0, padx=20, pady=20)

# ==================================================================================================
# ========================================= factory ================================================
# ==================================================================================================
params = []
autofill_num = 0


# ========================================= callbacks ==============================================
def choose_file_button_callback():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-16') as file:
                text = file.read()
        except Exception as e:
            if on_off == "ON":
                response_frame.insert('0.0', e)
            else:
                response_frame.insert('0.0', "FAIL!!")
        lines = text.split("\n")
        for line in lines:
            sections = line.split(' ')
            params.append(sections)

    delete_all()

    global autofill_num
    autofill_num = 0
    try:
        delete_all()
        setSN_entry.insert("0", params[autofill_num][0])
        setVidCode_entry.insert("0", params[autofill_num][1])
        setDpsCode_entry.insert("0", params[autofill_num][2])
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!")


def autofill_next_button_callback():
    delete_all()
    global autofill_num
    autofill_num += 1
    if autofill_num == len(params):
        autofill_num = 0
    try:
        setSN_entry.insert("0", params[autofill_num][0])
        setVidCode_entry.insert("0", params[autofill_num][1])
        setDpsCode_entry.insert("0", params[autofill_num][2])
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!")


def autofill_last_button_callback():
    delete_all()
    global autofill_num
    autofill_num -= 1
    if autofill_num == -1:
        autofill_num = len(params) - 1
    try:
        setSN_entry.insert("0", params[autofill_num][0])
        setVidCode_entry.insert("0", params[autofill_num][1])
        setDpsCode_entry.insert("0", params[autofill_num][2])
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!")


def factory_submit_button_callback():
    IP_ADDRESS = IP_Address_entry.get()
    response_frame.delete("0.0", "10000.10000")
    keys = {"setSn": setSN_entry.get(), "setVidCode": setVidCode_entry.get(), "setDpsCode": setDpsCode_entry.get()}
    try:
        response = requests.get(
            f"http://{IP_ADDRESS}/factory", params=keys, timeout=1)

        if response.status_code == 200:
            if on_off == "ON":
                content = response.text
                response_frame.insert("0.0", content)
            else:
                response_frame.insert("0.0", "SUCCESS!")
        else:
            response_frame.insert("0.0", "FAIL!")
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!")


# ========================================= elements ================================================
# choose file
choose_file_button = ctk.CTkButton(tabview.tab("factory"), text='選擇檔案', width=button_width, height=button_height,
                                   command=choose_file_button_callback)
choose_file_button.grid(row=0, column=1, padx=padx, pady=10)

# autofill label
autofill_label = ctk.CTkLabel(tabview.tab("factory"), text='自動填入:', width=40, height=button_height)
autofill_label.grid(row=1, column=0, padx=padx, pady=pady, sticky='nse')
# autofill lasts
autofill_lasts_button = ctk.CTkButton(tabview.tab("factory"), text='<<', width=40, height=button_height,
                                      command=autofill_last_button_callback)
autofill_lasts_button.grid(row=1, column=1, padx=padx, pady=pady, sticky='nsw')

# autofill next
autofill_next_button = ctk.CTkButton(tabview.tab("factory"), text='>>', width=40, height=button_height,
                                     command=autofill_next_button_callback)
autofill_next_button.grid(row=1, column=1, padx=padx, pady=pady, sticky='nse')

# setSN
setSN_label = ctk.CTkLabel(tabview.tab("factory"), text="setSN:", width=60, font=font)
setSN_label.grid(row=2, column=0, padx=20, pady=20, sticky="nse")

setSN_entry = ctk.CTkEntry(tabview.tab("factory"), width=100, height=20, border_width=2,
                           corner_radius=0)
setSN_entry.grid(row=2, column=1, padx=20, pady=20, sticky='nsw')
setSN_entry.configure(placeholder_text="")

# setVidCode
setVidCode_label = ctk.CTkLabel(tabview.tab("factory"), text="setVidCode:", width=60, font=font)
setVidCode_label.grid(row=3, column=0, padx=20, pady=20, sticky="nse")

setVidCode_entry = ctk.CTkEntry(tabview.tab("factory"), width=100, height=20, border_width=2,
                                corner_radius=0)
setVidCode_entry.grid(row=3, column=1, padx=20, pady=20, sticky='nsw')
setVidCode_entry.configure(placeholder_text="")

# setDpsCode
setDpsCode_label = ctk.CTkLabel(tabview.tab("factory"), text="SetDpsCode:", width=60, font=font)
setDpsCode_label.grid(row=4, column=0, padx=20, pady=20, sticky="nse")

setDpsCode_entry = ctk.CTkEntry(tabview.tab("factory"), width=100, height=20, border_width=2,
                                corner_radius=0)
setDpsCode_entry.grid(row=4, column=1, padx=20, pady=20, sticky='nsw')
setDpsCode_entry.configure(placeholder_text="")

# submit
factory_submit_button = ctk.CTkButton(tabview.tab("factory"), text="submit", width=button_width, height=button_height,
                                      command=factory_submit_button_callback)
factory_submit_button.grid(row=5, column=1, padx=20, pady=20)


# ==================================================================================================
# =========================================== setdb ================================================
# ==================================================================================================

# ========================================= callbacks ==============================================
def setdb_submit_button_callback():
    IP_ADDRESS = IP_Address_entry.get()
    response_frame.delete('0.0', '10000.10000')
    keys = {"setvmcenlevel": setvmcenlevel_entry.get()}
    try:
        response = requests.get(f"http://{IP_ADDRESS}/setdb", params=keys, timeout=1)
        if response.status_code == 200:
            if on_off == "ON":
                content = response.text
                response_frame.insert("0.0", content)
            else:
                response_frame.insert("0.0", "SUCCESS!")
        else:
            response_frame.insert("0.0", "FAIL!!")
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!!")


# ========================================= elements ================================================
# setvmcenlevel
setvmcenlevel_label = ctk.CTkLabel(tabview.tab("setdb"), text="setvmcenlevel:", width=60, font=font)
setvmcenlevel_label.grid(row=0, column=0, padx=20, pady=20)

setvmcenlevel_entry = ctk.CTkEntry(tabview.tab("setdb"), width=button_width, height=button_height, border_width=1,
                                   corner_radius=0)
setvmcenlevel_entry.grid(row=0, column=1, padx=20, pady=20, sticky='nsw')
setvmcenlevel_entry.insert("0", "0")
setvmcenlevel_entry.configure(state="disabled")
# submit
setdb_submit_button = ctk.CTkButton(tabview.tab("setdb"), text="submit", width=button_width, height=button_height,
                                    command=setdb_submit_button_callback)
setdb_submit_button.grid(row=2, column=1, padx=20, pady=20)

# ==================================================================================================
# ========================================= IP ADDRESS =============================================
# ==================================================================================================

# ======================================== elements ================================================
IP_Address_label = ctk.CTkLabel(root, text="IP Address", width=button_width, font=font)
IP_Address_label.grid(row=1, column=0, padx=20, pady=20, sticky="nsw")

IP_Address_entry = ctk.CTkEntry(root, width=120, height=20, border_width=2,
                                corner_radius=0)
IP_Address_entry.grid(row=1, column=0, padx=20, pady=20, sticky="nse")
IP_Address_entry.configure(placeholder_text="192.168.5.5")
IP_Address_entry.insert("0", "192.168.5.5")

# ==================================================================================================
# ========================================= IP ADDRESS =============================================
# ==================================================================================================

# ======================================== elements ================================================
# version display
version_var = ctk.StringVar(value=f'v{version}')
version_label = ctk.CTkLabel(root, textvariable=version_var, width=button_width, font=font)
version_label.grid(row=1, column=1, padx=padx, pady=pady, sticky='nse')

root.mainloop()
