import sys
import os
import cv2
import time
import matplotlib.pyplot as plt

def check_blackratio(checkimg):
    manual_count = [0, 0]  # その画像の色のピクセル数(黒,白)
    w, h = checkimg.shape
    total_pixels = 0
    for y in range(0, h, int(h / 100)):
        for x in range(0, w, int(w / 100)):
            RGB = (checkimg[x, y])  # グレースケールだから情報がひとつだけ?
            if RGB == 255:
                manual_count[1] += 1
            else:
                manual_count[0] += 1
            total_pixels += 1
    return 100 * float(manual_count[0]) / total_pixels


def get_binary_kernel(path):
    print("入力ファイル:" + path)
    # グレースケールで画像を読み込む.
    gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    binary_data = []
    best_n = 0
    phase = 0
    pre_black_ratio = None
    black_ratio = 0
    pre_abs = None
    for n in range(255, 150, -5):
        ret3, binary = cv2.threshold(gray, n, 255, cv2.THRESH_BINARY)
        black_ratio = check_blackratio(binary)
        binary_data.append(black_ratio)
        if pre_black_ratio is None:
            pre_black_ratio = black_ratio
            continue
        if phase is 0 and abs(pre_black_ratio - black_ratio) > 0:
            phase = 1
        elif phase is 1 and pre_abs > abs(pre_black_ratio - black_ratio):
            phase = 2
        elif phase is 2 and abs(pre_black_ratio - black_ratio) < 1:
            phase = 3
            best_n = n - 5
        pre_abs = abs(pre_black_ratio - black_ratio)
        pre_black_ratio = black_ratio
    print("閾値:" + str(best_n))
    plt.plot(list(range(255, 150, -5)), binary_data)  # グラフ
    plt.show()

    median_data = []
    best_k = 1
    c = 0
    for k in range(1, 21, 2):
        blur = cv2.medianBlur(gray, k)
        ret3, binary = cv2.threshold(blur, best_n, 255, cv2.THRESH_BINARY)
        black_ratio = check_blackratio(binary)
        median_data.append(black_ratio)
        if c is 0 and k is not 1 and abs(pre_abs - abs(pre_black_ratio - black_ratio)) > 0.1:
            c = 1
            best_k = k
            continue
        pre_abs = abs(pre_black_ratio - black_ratio)
        pre_black_ratio = black_ratio
    print("カーネルサイズ:" + str(best_k))
    plt.plot(list(range(1, 21, 2)), median_data)  # グラフ
    plt.show()

# 直接やるやつ
if len(sys.argv) == 2:
    start_time = time.perf_counter()  # 計測開始
    original_img_path = "sample_inputs/clean_line_drawings/" + sys.argv[1]
    get_binary_kernel(original_img_path)
