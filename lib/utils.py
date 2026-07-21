import difflib
import logging
import re

# class Config:
#     def __init__(self,path):
#         with open(path,'r') as f:
#             self.data=load(f)
#     def get(self,args):


def clean_spaces(string):           #add logging for situations where it is not string, so there wont be again errors with silent 
                                    #handling of pd.Series
    if not isinstance(string,str):          
        return string
    string=string.strip()
    string=re.sub(r'\s+',' ',string)
    return string

def color_diff_visible(a, b):
    # Replace the space character with a visible symbol (like '␣' or '·')
    for char in difflib.ndiff(a, b):
        # Determine the character to display
        display_char = '␣' if char[2] == ' ' else char[2]
        
        # Apply color based on the diff status
        if char[0] == '-':
            print(f'\033[91m{display_char}\033[0m', end='')  # Red
        elif char[0] == '+':
            print(f'\033[92m{display_char}\033[0m', end='')  # Green
        else:
            print(display_char, end='')  # No color
    print()  # Newline at the end

def create_logger():
    logging.basicConfig(filename='logs.log', level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    return logger

