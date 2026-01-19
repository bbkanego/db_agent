import os
from sys import exc_info

def read_file(path):
    absolute_path = os.path.abspath(path)
    print(f'------->>>>>>> The absolute path is {absolute_path}')
    try:
        with open(absolute_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print('File not found', exc_info())
    except Exception as e:
        print('Exception occurred', exc_info())
    finally:
        file.close()