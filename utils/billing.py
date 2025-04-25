from datetime import datetime

def calculate_charges(entry_time_str):
    entry_time = datetime.fromisoformat(entry_time_str)
    now = datetime.now()
    duration = (now - entry_time).total_seconds() / 3600  # in hours
    if duration <= 1:
        return 0
    else:
        return int((duration - 1) * 60)  # ₹60/hour after 1st hour
