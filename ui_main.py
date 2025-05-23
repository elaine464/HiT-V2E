
# ui_main.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QComboBox, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

class EventCameraUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Camera Upper - VID2E (GPU optimisation)")
        self.setGeometry(50, 50, 1920, 1080)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # —— 左侧图像展示区 —— #
        image_layout = QVBoxLayout()

        self.label_raw = QLabel("Raw Image")
        self.label_raw.setMinimumSize(1280, 720)
        self.label_raw.setStyleSheet("background-color: black;")
        self.label_raw.setFrameStyle(QFrame.Box)
        self.label_raw.setAlignment(Qt.AlignCenter)

        self.label_event = QLabel("Event Image")
        self.label_event.setMinimumSize(1280, 720)
        self.label_event.setStyleSheet("background-color: black;")
        self.label_event.setFrameStyle(QFrame.Box)
        self.label_event.setAlignment(Qt.AlignCenter)

        image_layout.addWidget(self.label_raw)
        image_layout.addWidget(self.label_event)
        main_layout.addLayout(image_layout, 5)

        # —— 右侧控制区 —— #
        control_panel = QVBoxLayout()

        # 滑块：阈值与衰减
        self.threshold_slider    = self._create_slider("Brightness Change Threshold", control_panel, max_val=255, init_val=20)
        self.time_window_slider  = self._create_slider("Event Frame Period (ms)", control_panel, max_val=50,  init_val=5)
        self.decay_slider        = self._create_slider("Time Decay Factor", control_panel, max_val=50,  init_val=10)

        # 背景色选择
        control_panel.addWidget(QLabel("Background Colour Selection："))
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["White Background", "Black Background", "Gray Background"])
        control_panel.addWidget(self.bg_combo)

        # 摄像头控制按钮
        self.start_cam_btn = QPushButton("▶ Turn On The Camera.")
        self.stop_cam_btn  = QPushButton("■ Turn Off The Camera.")
        control_panel.addWidget(self.start_cam_btn)
        control_panel.addWidget(self.stop_cam_btn)

        # 保存事件日志按钮
        self.save_csv_btn = QPushButton("📄 Save CSV")
        self.save_npz_btn = QPushButton("📦 Save NPZ")
        control_panel.addWidget(self.save_csv_btn)
        control_panel.addWidget(self.save_npz_btn)

        # 【新增】帧率实时显示
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #e63946;")
        control_panel.addWidget(self.fps_label)

        # 事件速率显示（保留原有功能）
        self.event_rate_label = QLabel("Event Rates：0 events/sec")
        self.event_rate_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #0077cc;")
        control_panel.addWidget(self.event_rate_label)

        # 完成布局
        main_layout.addLayout(control_panel, 1)
        self.setLayout(main_layout)

    def _create_slider(self, name, layout, max_val=100, init_val=15):
        """
        通用滑块生成函数
        name:     滑块名称
        layout:   所属布局
        max_val:  最大值
        init_val: 初始值
        """
        label = QLabel(f"{name}：{init_val}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(max_val)
        slider.setValue(init_val)
        slider.setSingleStep(1)
        slider.setTracking(True)
        slider.setPageStep(1)
        slider.valueChanged.connect(lambda val: label.setText(f"{name}：{val}"))
        layout.addWidget(label)
        layout.addWidget(slider)
        return slider
