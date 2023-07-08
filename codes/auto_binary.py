import sys
import os
import cv2
import time

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

    n = 255
    phase = 0
    pre_black_ratio = None
    black_ratio = 0
    pre_abs = None
    while phase < 3:
        ret3, binary = cv2.threshold(gray, n, 255, cv2.THRESH_BINARY)
        black_ratio = check_blackratio(binary)
        if pre_black_ratio is None:
            pre_black_ratio = black_ratio
            continue
        if phase is 0 and abs(pre_black_ratio - black_ratio) > 0:
            phase = 1
        elif phase is 1 and pre_abs > abs(pre_black_ratio - black_ratio):
            phase = 2
        elif phase is 2 and abs(pre_black_ratio - black_ratio) < 1:
            phase = 3
        pre_abs = abs(pre_black_ratio - black_ratio)
        pre_black_ratio = black_ratio
        n -= 5
    print("閾値:" + str(n))

    k = 1
    c = 0
    while c < 1:
        k += 2
        blur = cv2.medianBlur(gray, k)
        ret3, binary = cv2.threshold(blur, n, 255, cv2.THRESH_BINARY)
        black_ratio = check_blackratio(binary)
        if abs(pre_abs - abs(pre_black_ratio - black_ratio)) > 0.1:
            c += 1
            continue
        pre_abs = abs(pre_black_ratio - black_ratio)
        pre_black_ratio = black_ratio
    print("カーネルサイズ:" + str(k))
    return n, k


# 直接やるやつ
if len(sys.argv) == 2:
    start_time = time.perf_counter()  # 計測開始
    original_img_path = "sample_inputs/clean_line_drawings/" + sys.argv[1]
    binary, median = get_binary_kernel(original_img_path)
    gray = cv2.imread(original_img_path, cv2.IMREAD_GRAYSCALE)
    blur = cv2.medianBlur(gray, median)
    ret3, get_image = cv2.threshold(blur, binary, 255, cv2.THRESH_BINARY)
    save_file = "sample_inputs/clean_line_drawings/" + os.path.splitext(sys.argv[1])[0] + \
                "_m" + str(median,) + "b" + str(binary,) + ".png"
    cv2.imwrite(save_file, get_image)
    # 終了時刻
    end_time = time.perf_counter()
    # 差を出力
    processing_time = end_time - start_time
    print("processing_time: " + str(processing_time) + "\n")
