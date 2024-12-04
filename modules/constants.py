from os import path
from datetime import datetime
import json

def get_date_str() -> str:
    return datetime.now().strftime("%d-%m-%Y %H.%M.%S")

def load_json(filepath):
    if path.exists(filepath):
        with open(filepath, 'r',encoding='utf-8') as f:
            return json.load(f)
    return {}


SETTINGS = load_json(path.abspath('data/settings.json'))

# DATABASE
USERS_TABLE = 'users'
INFO_TABLE  = 'info'

TABLES_DICT = {
    USERS_TABLE: {
        'id':       'INTEGER PRIMARY KEY', 
        'username': 'TEXT', 

        'stage':  'TEXT', 
        'region': 'TEXT',
        'brand':  'TEXT',

        'born_date':        'TEXT', 
        'last_action_date': 'TEXT',
        },
    }

STAGE_ZERO =          "ZERO"
STAGE_REGION_CHOSEN = "REGION"
STAGE_BRAND_CHOSEN =  "BRAND"