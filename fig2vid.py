import cv2
import os
from natsort import natsorted  # pip install natsort

def bmp_folder_to_video(image_folder: str,
                        output_path: str,
                        fps: int = 30,
                        codec: str = 'mp4v'):
    """
    Assemble all BMP images in the specified folder into an MP4 video at 30 FPS.

    :param image_folder: Path to the folder containing BMP images
    :param output_path: Path for the output .mp4 video file (e.g. output.mp4)
    :param fps: Frames per second (default: 30)
    :param codec: FourCC video codec (default 'mp4v' for MP4)
    """
    # 1. List all BMP files and sort them naturally
    files = [f for f in os.listdir(image_folder) if f.lower().endswith('.bmp')]
    files = natsorted(files)
    if not files:
        raise FileNotFoundError(f"No BMP files found in directory: {image_folder}")

    # 2. Read the first image to get frame size
    first_img_path = os.path.join(image_folder, files[0])
    frame = cv2.imread(first_img_path)
    if frame is None:
        raise IOError(f"Cannot read image: {first_img_path}")
    height, width = frame.shape[:2]

    # 3. Create VideoWriter for MP4
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 4. Write each frame
    for fname in files:
        img_path = os.path.join(image_folder, fname)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: skipping unreadable file {img_path}")
            continue
        # If sizes differ, uncomment to resize:
        # img = cv2.resize(img, (width, height))
        video_writer.write(img)

    # 5. Release resources
    video_writer.release()
    print(f"Video successfully created: {output_path}")


if __name__ == "__main__":
    # Example usage
    src_folder = r"C:\Users\18795\Desktop\image"
    out_video = r"C:\Users\18795\Desktop\output.mp4"
    bmp_folder_to_video(src_folder, out_video, fps=30, codec='mp4v')
