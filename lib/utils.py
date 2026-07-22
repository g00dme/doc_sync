import difflib
import logging
import re

import json

logger = logging.getLogger(__name__)

def clean_spaces(string):             #add logging for situations where it is not string, so there wont be again errors with silent                  
    if not isinstance(string,str):    #handling of pd.Series       
        logger.warning(f'{type(string)}')
        return string
    string=string.strip()
    string=re.sub(r'\s+',' ',string)
    return string

def load_config(path):
    try:
        with open(path,'r') as f:
            config=json.load(f)
            logger.info('loaded config')
            logger.debug(config)
            return config
    except FileNotFoundError:
        logger.error(f'Fine not found: {path}')
    except json.JSONDecodeError:
        logger.error(f'{path} has invalid json format')


def color_diff_visible(a, b):
    # Replace the space character with a visible symbol (like '␣' or '·')
    line=''
    for char in difflib.ndiff(a, b):
        # Determine the character to display
        display_char = '␣' if char[2] == ' ' else char[2]
        display_char = '\\t' if char[2] == '\t' else char[2]
        display_char = '\\n' if char[2] == '\n' else char[2]

        # Apply color based on the diff status
        if char[0] == '-':
            line+=f'\033[91m{display_char}\033[0m'  # Red
        elif char[0] == '+':
            line+=f'\033[92m{display_char}\033[0m'  # Green
        else:
            line+=display_char  # No color
    return line  # Newline at the end

def configure_logger():
    logging.basicConfig(filename='logs.log', level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    return logger

