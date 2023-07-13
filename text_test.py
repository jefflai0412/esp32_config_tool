import re

# 假設文檔內容存儲在一個字符串變數中
document = '''
autofill_num: 0
file_path:TEST_CODE.txt
'''

# 使用正則表達式進行匹配和替換
new_file_path = "NEW_FILE.txt"
document = re.sub(r'(file_path:\s*)(\w+\.txt)', r'\1' + new_file_path, document)

# 輸出更改後的文檔內容
print(document)
