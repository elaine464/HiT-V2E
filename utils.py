# utils.py
import numpy as np
import cv2
from PyQt5.QtGui import QImage, QPixmap

def get_background_canvas(height, width, color=(255, 255, 255)):
    """
    获取指定背景色的空图像
    """
    canvas = np.ones((height, width, 3), dtype=np.uint8)
    canvas *= np.array(color, dtype=np.uint8)
    return canvas

def cv2_to_qpixmap(cv_img_bgr):
    """
    OpenCV图像转QPixmap（用于PyQt显示）
    """
    h, w, ch = cv_img_bgr.shape
    img_rgb = cv2.cvtColor(cv_img_bgr, cv2.COLOR_BGR2RGB)
    qimg = QImage(img_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)
