autofill_num_path = "autofill_num.txt"  # Replace with the path to your text file
autofill_num = 11
engineer_mode = "ON"

def autofill_num_config(RW):
    global autofill_num
    global engineer_mode

    if RW == 'R':
        try:
            with open(autofill_num_path, "r") as file:
                autofill_num = file.read()
        except FileNotFoundError:
            with open(autofill_num_path, "w") as file:
                file.write('0')
    else:
        try:
            with open(autofill_num_path, "w") as file:
                autofill_num = file.read()
        except Exception as e:
            if engineer_mode == "ON":
                response_frame.insert('0.0', e)
            else:
                response_frame.insert('0.0', "FAIL!!")


autofill_num_config()
