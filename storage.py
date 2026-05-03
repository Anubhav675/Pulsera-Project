import ujson
import os
import time

FILENAME = "history.json"

def save_result(bpm, rmssd, sdnn):
    try:
        data = load_history()
    except:
        data = []

    new_entry = {
        "bpm": bpm,
        "rmssd": rmssd,
        "sdnn": sdnn,
        "timestamp": time.time()
    }

    data.insert(0, new_entry)

    if len(data) > 10:
        data = data[:10]

    try:
        with open(FILENAME, "w") as f:
            ujson.dump(data, f)
    except Exception as e:
        print("Save Error:", e)

def load_history():
    if FILENAME not in os.listdir():
        return []

    try:
        with open(FILENAME, "r") as f:
            return ujson.load(f)
    except:
        return []