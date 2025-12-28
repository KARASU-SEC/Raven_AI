import os
import json
import sys

# Добавляем корень проекта в sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'settings.json')
COMMANDS_PATH = os.path.join(BASE_DIR, 'config', 'commands_map.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_commands():
    try:
        with open(COMMANDS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"commands": {}}
