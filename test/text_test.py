import re
# # 假設文檔內容存儲在一個字符串變數中
# file_path = r'test/test.txt'
# with open(file_path, 'r') as file:
#     document = file.read()
#
# # 使用字串操作來提取 file_path 的值
# file_path_line = document.split('\n')[1]  # 按換行符分割文檔內容，取第二行
# file_path_value = file_path_line.split(':')[1].strip()  # 按冒號分割行，取第二部分並去除前後空格
#
# print("file_path:", file_path_value)

# status_path = r'status_test.txt'
# file_path = '../TEST_CODE.txt'
# with open(status_path, "w") as file:
#     file.write('autofill_num:0\n' + f'file_path:{file_path}')
# with open(status_path, 'r') as file:
#     print(file.read())


# with open(status_path, 'r') as file:
#     print(file.read())

status_path = r'../status.txt'  # status record autofill_num and code_path
with open(status_path, "r") as file:
    status = file.read()

lines = status.split('\n')

# Extract autofill_num
autofill_num_line = lines[0]
index = autofill_num_line.find("autofill_num")
autofill_num = autofill_num_line[index + len("autofill_num"):].strip()

# Extract code_path
code_path_line = lines[1]
index = code_path_line.find("code_path")
code_path = code_path_line[index + len("code_path"):].strip()

print('autofill_num:', autofill_num)
print(code_path)
