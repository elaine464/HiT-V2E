# event_saver.py
import numpy as np
import csv
import time

def save_event_csv(event_list, path):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'timestamp', 'polarity'])
        for event in event_list:
            writer.writerow(event)

def save_event_npz(event_list, path):
    x = np.array([e[0] for e in event_list])
    y = np.array([e[1] for e in event_list])
    t = np.array([e[2] for e in event_list])
    p = np.array([e[3] for e in event_list])
    np.savez_compressed(path, x=x, y=y, t=t, p=p)

def generate_timestamp_filename(prefix, ext):
    ts = time.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"
