import re
import subprocess
import time
from tkinter import filedialog
import customtkinter as ctk
import requests

# ========================================== settings ==============================================
version = "3.9.0"
status_path = r'status.txt'  # status record autofill_num and code_path
autofill_num = 0
code_path = 'None'
board_version = 'CUK12'

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.geometry("700x600")
root.title(f"esp32 config v{version}")
font = ("Roboto", 14)
button_width = 100
button_height = 30
padx = 20
pady = 15

# ================================== frequently used function =======================================
engineer_mode = 'OFF'


def status_config(RW):
    global autofill_num
    global code_path
    global engineer_mode
    global board_version

    if RW == 'R':
        try:
            print("here code path: ", code_path)
            with open(status_path, "r") as file:
                status = file.read()
                lines = status.split('\n')
                # Extract autofill_num
                autofill_num_line = lines[0]
                autofill_num_line_index = autofill_num_line.find("autofill_num")
                autofill_num = int(autofill_num_line[autofill_num_line_index + len("autofill_num"):].strip())

                # Extract code_path
                code_path_line = lines[1]
                code_path_line_index = code_path_line.find("code_path")
                code_path = code_path_line[code_path_line_index + len("code_path"):].strip()
                print("status config code_path:", code_path)

                # Extract board_version
                board_version_line = lines[2]
                board_version_line_index = board_version_line.find("board_version")
                board_version = board_version[board_version_line_index + len("board_version"):].strip()


        except FileNotFoundError:
            autofill_num = 0
            with open(status_path, "w") as file:
                file.write(f'autofill_num 0\ncode_path {code_path}\nboard_version {board_version}')

        except Exception as e:
            if engineer_mode == "ON":
                response_frame.insert('0.0', f'status_config("R"): {e}')
            else:
                response_frame.insert('0.0', "status_config("R"): FAIL!!")
    else:
        try:
            with open(status_path, "w") as file:
                file.write(f'autofill_num {autofill_num}\ncode_path {code_path}')
                print("code path: ", code_path)
        except Exception as e:
            if engineer_mode == "ON":
                response_frame.insert('0.0', f"file write: {e}")
            else:
                response_frame.insert('0.0', "FAIL!!")


def delete_all():
    response_frame.delete("0.0", '10000.10000')
    setSN_entry.delete('0', '100')
    setVidCode_entry.delete('0', '100')
    setDpsCode_entry.delete('0', '100')


def autofill():
    global autofill_num
    delete_all()
    try:
        setSN_entry.insert("0", params[autofill_num][0])
        setVidCode_entry.insert("0", params[autofill_num][1])
        setDpsCode_entry.insert("0", params[autofill_num][2])
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "自動填入: FAIL!")


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
# ========================================= settings ============================================
# ==================================================================================================
on_off = "OFF"


# ========================================= callbacks ==============================================
def mode_switch_callback():
    global on_off
    if on_off == "OFF":
        on_off = "ON"
    else:
        on_off = "OFF"
    mode_switch.configure(text=f"工程模式:{on_off}")


def board_version_menu_callback(choice):
    global board_version
    board_version = choice


# ========================================= elements ================================================
mode_switch = ctk.CTkSwitch(master=root, text=f"工程模式:{on_off}", height=button_height, command=mode_switch_callback)
mode_switch.grid(row=0, column=1, padx=(20, 10), pady=20, sticky="nw")

board_version_menu = ctk.CTkOptionMenu(master=root, values=["CUK12", "CUK22"], width=button_width, height=button_height,
                                       command=board_version_menu_callback)
board_version_menu.grid(row=0, column=1, padx=(20, 10), pady=20, sticky="ne")

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
    for widgets in SSID_display_frame.winfo_children():
        widgets.destroy()
    SSID_display_frame.scroll_to_top()
    result = "None"
    response_frame.delete('0.0', '1000.1000')
    global ssids
    # Command to scan Wi-Fi networks
    subprocess.run('netsh interface set interface name="WiFi" admin="disabled"', shell=True)
    subprocess.run('netsh interface set interface name="WiFi" admin="enabled"', shell=True)

    command = "netsh wlan show networks mode=Bssid"

    # Execute the command and capture the output
    try:
        result = subprocess.check_output(command, shell=True, encoding='latin-1')
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!!")

    # Use regular expression to extract SSID names
    ssids = re.findall(r'SSID\s\d+\s:\s(\S+)', result)

    # Filter SSIDs that start with "1VY" or "CUK"
    filtered_ssids = [ssid for ssid in ssids if
                      ssid.startswith("1YV") or ssid.startswith("CUK") or ssid.startswith("VUK")]

    ssid_buttons = {}
    for (i, ssid) in enumerate(filtered_ssids):
        # print(i, ssid)
        ssid_button = 'ssid_button' + str(i)
        ssid_buttons[ssid_button] = ctk.CTkButton(SSID_display_frame, text=ssid, width=150,
                                                  height=button_height,
                                                  command=lambda ssid=ssid: ssid_button_callback(ssid), font=font)
        ssid_buttons[ssid_button].grid(row=i, column=0, padx=20, pady=3)


def ssid_button_callback(network_name):
    response_frame.delete('0.0', '1000.1000')
    # network_name = "None"
    # Command to connect to Wi-Fi network
    command = f'netsh wlan connect name="{network_name}" ssid="{network_name}" interface="Wi-Fi"'
    try:
        # Execute the command
        subprocess.call(command, shell=True)
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "FAIL!!")

    # Wait for a brief moment to allow the connection to establish
    time.sleep(2)

    # Run the netsh command to get the current Wi-Fi network name
    result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
    output = result.stdout
    # Extract the network name from the output
    for line in output.splitlines():
        if "SSID" in line:
            network_name = line.split(":")[1].strip()
            break
    response_frame.insert('0.0', f'已連接至: {network_name}')


# ========================================= elements ================================================
scan_button = ctk.CTkButton(tabview.tab("WIFI"), text='掃描WiFi', width=button_width, height=button_height,
                            command=scan_button_callback, font=font)
scan_button.grid(row=0, column=0, padx=20, pady=20)

SSID_display_frame = ctk.CTkScrollableFrame(tabview.tab("WIFI"), width=button_width * 2, height=250)
SSID_display_frame.grid(row=1, column=0, padx=0, pady=0)
SSID_display_frame.grid_columnconfigure(0, weight=1)

# ==================================================================================================
# ========================================= factory ================================================
# ==================================================================================================
params = []
text = 'None'
encoding = 'utf-8'

# autofill_num = 0


# ========================================= callbacks ==============================================
def choose_file_button_callback():
    global code_path
    global text
    global autofill_num
    global params

    delete_all()
    code_path = filedialog.askopenfilename()
    print("code_path", code_path)
    status_config("W")
    status_config("R")  # read the current autofill_num
    print("code_path", code_path)

    if code_path:
        params = []  # clear the list
        autofill_num = 0
        print("choose file: ", code_path)
        print("autofill_num: ", autofill_num)
        try:
            with open(code_path, 'r', encoding=encoding) as file:
                text = file.read()
        except Exception as e:
            if on_off == "ON":
                response_frame.insert('0.0', f"選擇檔案: {e}")
            else:
                response_frame.insert('0.0', "選擇檔案: FAIL!!")
        lines = text.split("\n")
        for line in lines:
            sections = line.split(' ')
            params.append(sections)

    delete_all()

    try:
        delete_all()
        setSN_entry.insert("0", params[autofill_num][0])
        setVidCode_entry.insert("0", params[autofill_num][1])
        setDpsCode_entry.insert("0", params[autofill_num][2])
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', f"選擇檔案_自動填入: {e}")
        else:
            response_frame.insert('0.0', "選擇檔案_自動填入: FAIL!")


def encoder_menu_callback(choice):
    global encoding
    encoding = choice


def autofill_next_button_callback():
    delete_all()
    status_config('R')
    global autofill_num
    autofill_num += 1
    if autofill_num == len(params):
        autofill_num = 0
    autofill()
    status_config('W')


def autofill_last_button_callback():
    delete_all()
    status_config('R')
    global autofill_num
    autofill_num -= 1
    if autofill_num == -1:
        autofill_num = len(params) - 1
    autofill()
    status_config('W')


def setSN_handle_enter(*kwarg):
    print("enter handler")
    global text
    global autofill_num
    setSN_value = setSN_entry.get()
    line_number = None
    # Opening the file and storing its data into the variable lines
    lines = text.splitlines()
    # Going over each line of the file
    for line_num, line in enumerate(lines, 1):
        # Condition true if the key exists in the line
        # If true then display the line number
        if setSN_value in line:
            autofill_num = line_num - 1
    autofill()
    status_config('W')


def factory_submit_button_callback():
    status_config('R')
    global autofill_num
    IP_ADDRESS = IP_Address_entry.get()
    response_frame.delete("0.0", "10000.10000")
    keys = {"setSn": setSN_entry.get(), "setVidCode": setVidCode_entry.get(), "setDpsCode": setDpsCode_entry.get()}
    try:
        response = requests.get(
            f"http://{IP_ADDRESS}/factory", params=keys, timeout=1)

        if response.status_code == 200:
            autofill_next_button_callback()
            if on_off == "ON":
                content = response.text
                response_frame.insert("0.0", content)
            else:
                response_frame.insert("0.0", "factory: SUCCESS!")
            # tabview.set("setdb")
            # time.sleep(0.5)
            if board_version == "CUK22":
                setdb_submit_button_callback()
            tabview.set("WIFI")
        else:
            response_frame.insert("0.0", "factory: FAIL!")
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', f"factory: {e}")
        else:
            response_frame.insert('0.0', "factory: FAIL!")


# ========================================= elements ================================================
# choose file
choose_file_button = ctk.CTkButton(tabview.tab("factory"), text='選擇檔案', width=button_width, height=button_height,
                                   command=choose_file_button_callback)
choose_file_button.grid(row=0, column=0, padx=padx, pady=10)

# encoder
encoder_menu = ctk.CTkOptionMenu(tabview.tab("factory"), values=['utf-8', 'utf-16'], width=button_width,
                                 height=button_height,
                                 command=encoder_menu_callback)
encoder_menu.grid(row=0, column=1, padx=padx, pady=10)


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
setSN_entry.bind("<Return>", setSN_handle_enter)

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
                response_frame.insert("0.0", "setdb: SUCCESS!")

            time.sleep(0.5)
            tabview.set('WIFI')
        else:
            response_frame.insert("0.0", "setdb: FAIL!!")
    except Exception as e:
        if on_off == "ON":
            response_frame.insert('0.0', e)
        else:
            response_frame.insert('0.0', "setdb: FAIL!!")


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
