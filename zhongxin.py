import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

# ———– 用户设置 ———–
input_path      = "output.mp4"             # 输入视频路径（已裁剪）
output_path     = "output_annotated.avi"  # 带标注的视频输出路径
area_plot_path  = "area_plot.png"         # 面积折线图输出路径

gray_threshold  = 50      # 黑色区域阈值上限（0~255），越小越严格
# ——————————————

def circularity(area, perimeter):
    """计算轮廓圆度：4πA / P^2"""
    if perimeter == 0:
        return 0.0
    return 4 * math.pi * area / (perimeter * perimeter)

def main():
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"无法打开视频文件：{input_path}")
        return

    # 视频参数
    fps    = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out    = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    areas     = []
    circs     = []
    best_circ = 0.0
    best_frame_idx = 0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 转灰度并二值化：黑色区域→白（255），背景→黑（0）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, gray_threshold, 255, cv2.THRESH_BINARY_INV)

        # 查找所有外轮廓
        contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 最大面积轮廓
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            peri = cv2.arcLength(cnt, True)
            circ = circularity(area, peri)
        else:
            area = 0.0
            circ = 0.0

        areas.append(area)
        circs.append(circ)

        # 更新最佳圆度帧
        if circ > best_circ:
            best_circ = circ
            best_frame_idx = frame_idx

        # 在帧上绘制轮廓与数值
        if contours:
            cv2.drawContours(frame, [cnt], -1, (0,0,255), 2)
        cv2.putText(frame, f"Frame: {frame_idx}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"Area: {area:.1f}", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"Circ: {circ:.3f}", (10,90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        # 写入输出视频（无窗口显示）
        out.write(frame)
        frame_idx += 1

    # 释放视频资源
    cap.release()
    out.release()

    # 打印最接近圆形的帧号及圆度
    print(f"最接近圆形的帧号：{best_frame_idx}  (圆度={best_circ:.3f})")

    # 绘制、保存并展示面积折线图
    plt.figure(figsize=(10, 4))
    plt.plot(areas, linewidth=1)
    plt.xlabel("Frame Index")
    plt.ylabel("Black Region Area (pixels)")
    plt.title("Center Black Area over Frames")
    plt.tight_layout()
    plt.savefig(area_plot_path, dpi=150)
    plt.show()    # 弹出展示折线图
    plt.close()

if __name__ == "__main__":
    main()
