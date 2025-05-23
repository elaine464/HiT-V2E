# 文件：main.py
import sys
import time
import numpy as np
import cv2
import threading
import queue
import traceback
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal, QObject

from ui_main import EventCameraUI
from camera_stream import CameraStream
from event_generator import EventGenerator
from event_saver import save_event_csv, save_event_npz
from utils import get_background_canvas

class WorkerSignals(QObject):
    update_frame = pyqtSignal(np.ndarray, np.ndarray, float)

class CameraWorker(threading.Thread):
    def __init__(self, cam, generator, ui):
        super().__init__()
        self.cam = cam
        self.generator = generator
        self.ui = ui
        self.signals = WorkerSignals()
        self.running = False
        self.last_update_time = time.time()

        # —— 新增：队列缓存与 FPS 统计 —— #
        self.frame_queue = queue.Queue(maxsize=5)
        self.fps_time = time.time()
        self.frame_count = 0

    def run(self):
        self.running = True
        print("[CameraWorker] Camera thread started")
        while self.running:
            # 1) 读取一帧
            frame = self.cam.read()
            if frame is None:
                print("[CameraWorker] Unable to read camera frames")
                continue

            # 2) 入队缓冲
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

            # 3) FPS 统计
            self.frame_count += 1
            if time.time() - self.fps_time >= 1.0:
                fps = self.frame_count / (time.time() - self.fps_time)
                # 更新界面上的帧率显示
                self.ui.fps_label.setText(f"FPS: {fps:.2f}")
                self.fps_time = time.time()
                self.frame_count = 0

            # 4) 出队并处理
            proc_frame = self.frame_queue.get()

            try:
                # 固定处理流程
                proc_frame = cv2.resize(proc_frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
                gray_cpu = cv2.UMat(cv2.cvtColor(proc_frame, cv2.COLOR_BGR2GRAY)).get()
                threshold = self.ui.threshold_slider.value()
                decay     = self.ui.decay_slider.value()
                bg_color  = self.ui.color_map[self.ui.bg_combo.currentText()]

                events, event_img = self.generator.generate(
                    gray_cpu,
                    threshold=threshold,
                    decay=decay,
                    polarity_pos=True,
                    polarity_neg=True,
                    bg_color=bg_color
                )

                self.last_update_time = time.time()
                # 事件速率：events数 / 时间间隔
                rate = len(events) / max(1e-3, (time.time() - self.last_update_time))
                self.signals.update_frame.emit(proc_frame, event_img, rate)

            except Exception:
                print("[CameraWorker] 图像处理出错:")
                traceback.print_exc()

    def stop(self):
        self.running = False

class MainApp(EventCameraUI):
    def __init__(self):
        super().__init__()
        self.cam = None
        self.generator = EventGenerator()
        self.worker = None
        # 背景色映射
        self.color_map = {
            "White backgrounds": (255, 255, 255),
            "Black backgrounds": (0, 0, 0),
            "Gray backgrounds": (127, 127, 127)
        }
        # 按钮绑定
        self.start_cam_btn.clicked.connect(self.start_camera)
        self.stop_cam_btn.clicked.connect(self.stop_camera)
        self.save_csv_btn.clicked.connect(self._save_csv)
        self.save_npz_btn.clicked.connect(self._save_npz)

    def start_camera(self):
        if self.cam is None:
            try:
                self.cam = CameraStream()
                self.cam.set_resolution(1280, 720)
                print("[MainApp] 摄像头打开成功")
            except RuntimeError as e:
                QMessageBox.critical(self, "摄像头错误", str(e))
                return
        if self.worker is None:
            self.worker = CameraWorker(self.cam, self.generator, self)
            self.worker.signals.update_frame.connect(self.update_display)
            self.worker.start()

    def stop_camera(self):
        if self.worker:
            self.worker.stop()
            self.worker.join()
            self.worker = None
        if self.cam:
            self.cam.release()
            self.cam = None
        self.label_raw.clear()
        self.label_event.clear()
        self.fps_label.setText("FPS: 0")

    def update_display(self, frame, event_img, rate):
        # 原图 & 事件图 刷新
        self._set_image(self.label_raw, frame)
        self._set_image(self.label_event, event_img)
        # 事件速率显示
        self.fps_label.setText(f"Event rates：{rate:.1f} events/sec")

    def _set_image(self, label, img_bgr):
        img_resized = cv2.resize(img_bgr, (1280, 720))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        h, w, _ = img_resized.shape
        qimg = QImage(img_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))

    def _save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save event log as CSV", filter="CSV Files (*.csv)")
        if path:
            save_event_csv(self.generator.event_buffer.copy(), path)
            QMessageBox.information(self, "Save Successful", f"The event data has been saved to the：\n{path}")

    def _save_npz(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save event log as NPZ", filter="NPZ Files (*.npz)")
        if path:
            save_event_npz(self.generator.event_buffer.copy(), path)
            QMessageBox.information(self, "Save Successful", f"The event data has been saved to the：\n{path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainApp()

    def on_exit():
        print("[MainApp] 正在退出程序，释放资源...")
        if main_window.worker:
            main_window.worker.stop()
            main_window.worker.join()
        if main_window.cam:
            main_window.cam.release()
        print("[MainApp] 已完成资源释放")

    app.aboutToQuit.connect(on_exit)
    main_window.show()
    sys.exit(app.exec_())
