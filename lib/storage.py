import ujson
import os

HISTORY_FILE = "history.json"
MAX_ENTRIES = 5 

def save_result(bpm, rmssd, sdnn):
    data = load_history()
    new_entry = {
        "bpm": int(bpm),
        "rmssd": int(rmssd),
        "sdnn": int(sdnn)
    }
    data.insert(0, new_entry)
    data = data[:MAX_ENTRIES]
    try:
        with open(HISTORY_FILE, "w") as f:
            ujson.dump(data, f)
    except Exception as e:
        print("Storage Error:", e)

def load_history():
    try:
        if HISTORY_FILE in os.listdir():
            with open(HISTORY_FILE, "r") as f:
                return ujson.load(f)
        return []
    except:
        return []