import json
import os
from datetime import datetime

SESSION_FILE = "data/sessions.json"
BALANCE_FILE = "data/balance.json"

def _load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)
    with open(file_path, 'r') as f:
        return json.load(f)

def _save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def start_session(user_id, user_data):
    sessions = _load_json(SESSION_FILE)
    sessions[user_id] = {"entry_time": datetime.now().isoformat(), "data": user_data}
    _save_json(SESSION_FILE, sessions)

def end_session(user_id):
    sessions = _load_json(SESSION_FILE)
    if user_id in sessions:
        entry_time = sessions[user_id]["entry_time"]
        del sessions[user_id]
        _save_json(SESSION_FILE, sessions)
        return entry_time
    return None

def load_sessions():
    return _load_json(SESSION_FILE)

# Balance Functions
def get_user_balance(user_id):
    balances = _load_json(BALANCE_FILE)
    return balances.get(user_id, 0)

def add_balance(user_id, amount):
    balances = _load_json(BALANCE_FILE)
    balances[user_id] = balances.get(user_id, 0) + amount
    _save_json(BALANCE_FILE, balances)

def deduct_balance(user_id, amount):
    balances = _load_json(BALANCE_FILE)
    if balances.get(user_id, 0) >= amount:
        balances[user_id] -= amount
        _save_json(BALANCE_FILE, balances)
        return True
    return False
# utils/session.py

user_db = {}

def user_exists(user_id):
    return user_id in user_db

def register_user(user_id, data):
    user_db[user_id] = {"data": data, "balance": 0}
