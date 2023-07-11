params = []
def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-16') as file:
            text = file.read()
    except FileNotFoundError:
        print("File not found.")
    except PermissionError:
        print("Permission denied to open the file.")
    except Exception as e:
        print("An error occurred:", str(e))
    lines = text.split("\n")
    for line in lines:
        sections = line.split(' ')
        # print(sections)
        params.append(sections)

    print(params)


file_path = r'dpskey.txt'
read_text_file(file_path)


