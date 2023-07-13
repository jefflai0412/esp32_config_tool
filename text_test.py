autofill_num_path = r'autofill_num.txt'

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
        except Exception as e:
            if engineer_mode == "ON":
                response_frame.insert('0.0', e)
            else:
                response_frame.insert('0.0', "FAIL!!")
    else:
        try:
            with open(autofill_num_path, "w") as file:
                file.write(f'{autofill_num}')
        except Exception as e:
            if engineer_mode == "ON":
                response_frame.insert('0.0', e)
            else:
                response_frame.insert('0.0', "FAIL!!")
    print("autofill_num: ", autofill_num)