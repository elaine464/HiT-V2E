import cv2
import time
import numpy as np

from event_generator import EventGenerator
from event_saver import save_event_csv, save_event_npz

# ———– User Settings ———–
# Set your input/output paths and parameters here:
input_path  = r"C:\Users\18795\Desktop\output.mp4"
output_path = r"C:\Users\18795\Desktop\event_output.avi"

threshold   = 15       # gray-level difference threshold
decay       = 10       # time decay factor
bg          = 'white'  # 'white', 'black', or 'gray'

save_csv    = True
csv_path    = r"C:\Users\18795\Desktop\events.csv"

save_npz    = True
npz_path    = r"C:\Users\18795\Desktop\events.npz"
# —————————————————

def main():
    # Open video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: cannot open video file {input_path}")
        return

    # Video parameters (dynamic resolution)
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Output VideoWriter (XVID) at same resolution
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out    = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Background color map
    bg_map = {
        'white': (255, 255, 255),
        'black': (  0,   0,   0),
        'gray' : (127, 127, 127)
    }
    bg_color = bg_map.get(bg, (255,255,255))

    # Event generator and log storage
    generator  = EventGenerator()
    all_events = []

    frame_idx  = 0
    start_time = time.time()

    # Fixed internal resolution for the generator
    target_W, target_H = 1280, 720

    print("Starting processing, input:", input_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to gray and resize to generator's expected size
        gray_orig = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray_orig, (target_W, target_H))

        # Generate events & small event image
        events_small, event_img_small = generator.generate(
            gray,
            threshold=threshold,
            decay=decay,
            bg_color=bg_color
        )

        # Scale events back to original resolution
        scaled_events = []
        for x, y, p, t in events_small:
            x2 = int(x * (width  / target_W))
            y2 = int(y * (height / target_H))
            scaled_events.append((x2, y2, p, t))
        all_events.extend(scaled_events)

        # Resize event image back to original resolution and write
        event_img = cv2.resize(event_img_small, (width, height))
        out.write(event_img)

        frame_idx += 1
        if frame_idx % 50 == 0:
            elapsed = time.time() - start_time
            print(f"Processed {frame_idx} frames in {elapsed:.1f}s (avg FPS {frame_idx/elapsed:.2f})")

    cap.release()
    out.release()
    print("✔  Event video saved to:", output_path)

    if save_csv:
        save_event_csv(all_events, csv_path)
        print("✔  Events saved as CSV:", csv_path)
    if save_npz:
        save_event_npz(all_events, npz_path)
        print("✔  Events saved as NPZ:", npz_path)


if __name__ == '__main__':
    main()
