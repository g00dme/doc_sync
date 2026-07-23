import difflib
import logging
import re

import json

logger = logging.getLogger(__name__)
logger.propagate = True

def clean_spaces(string):             #add logging for situations where it is not string, so there wont be again errors with silent                  
    if not isinstance(string,str):    #handling of pd.Series       
        logger.debug(f'{type(string)}')
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


def diff_visible(a, b):
    diff=difflib.ndiff(a, b)

    line=''
    change=''
    for x in diff:
        change+=x[0]
        line+=x[2]

    line= line + '\n' + change 

    return line 

def configure_logger():
    logging.basicConfig(filename='logs.log', level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    return logger

