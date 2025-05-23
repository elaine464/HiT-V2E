# 文件：event_generator.py
import numpy as np
import time

class EventGenerator:
    def __init__(self):
        self.prev_gray = None
        self.event_buffer = []

    def generate(self, gray, threshold=15, decay=10,
                 polarity_pos=True, polarity_neg=True,
                 bg_color=(255, 255, 255)):

        assert gray.shape == (720, 1280), f"灰度图尺寸应为 1280×720，实际为 {gray.shape[::-1]}"

        h, w = gray.shape
        bg = np.array(bg_color, dtype=np.uint8)
        event_img = np.full((h, w, 3), bg, dtype=np.uint8)

        if self.prev_gray is None:
            self.prev_gray = gray.copy()
            return [], event_img

        # 计算差分
        diff = gray.astype(np.int16) - self.prev_gray.astype(np.int16)
        timestamp = time.time()

        # 矢量化：生成正/负掩码
        pos_mask = (diff > threshold) if polarity_pos else np.zeros_like(diff, dtype=bool)
        neg_mask = (diff < -threshold) if polarity_neg else np.zeros_like(diff, dtype=bool)

        # 绘制事件像素
        event_img[pos_mask] = [0, 0, 255]    # 红点：正极性
        event_img[neg_mask] = [255, 0, 0]    # 蓝点：负极性

        # 提取所有事件坐标
        y_pos, x_pos = np.where(pos_mask)
        y_neg, x_neg = np.where(neg_mask)

        # 构建事件列表
        events_pos = list(zip(x_pos, y_pos, [timestamp]*len(x_pos), [1]*len(x_pos)))
        events_neg = list(zip(x_neg, y_neg, [timestamp]*len(x_neg), [-1]*len(x_neg)))
        events = events_pos + events_neg

        # 更新状态
        self.prev_gray = gray.copy()
        self.event_buffer.extend(events)

        return events, event_img
