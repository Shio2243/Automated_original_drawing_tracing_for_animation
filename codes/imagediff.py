import sys
import cv2
import numpy as np
import os
import csv

args = sys.argv
trace_img_file = 'sample_inputs/trace/' + sys.argv[1] + '_self.png'
trace_img = cv2.imread(trace_img_file)
data = [["", "clean_d", "cleanup_w", "cleanup_b",  # d:差分 w:その内のはみ出し b:その内の欠如
         "pre_clean_d", "pre_cleanup_w", "pre_cleanup_b",
         "pre_clean_opti_d", "pre_cleanup_opti_w", "pre_cleanup_opti_b"]]
for n in range(10):
    output_file = 'outputs/sampling/clean_line_drawings__pretrain_clean_line_drawings/'\
                  + sys.argv[2] + '_' + str(n)+ '_pred.png'
    output_img = cv2.imread(output_file)
    diff_img = trace_img.astype(int) - output_img.astype(int)
    diff_img_center = np.floor_divide(diff_img, 2) + 128
    white_pixel = np.count_nonzero(diff_img_center > 128)
    white_ratio = white_pixel / diff_img.size * 100
    black_pixel = np.count_nonzero(diff_img_center < 128)
    black_ratio = black_pixel / diff_img.size * 100
    os.makedirs('diff/' + sys.argv[1] + '/cleanup', exist_ok=True)
    cv2.imwrite('diff/' + sys.argv[1] + '/cleanup/' + str(n) + '.png', diff_img_center)

    output_file2 = 'outputs/sampling/clean_line_drawings__pretrain_clean_line_drawings/' \
                   + sys.argv[3] + '_' + str(n) + '_pred.png'
    output_img2 = cv2.imread(output_file2)
    diff_img2 = trace_img.astype(int) - output_img2.astype(int)
    diff_img_center2 = np.floor_divide(diff_img2, 2) + 128
    white_pixel2 = np.count_nonzero(diff_img_center2 > 128)
    white_ratio2 = white_pixel2 / diff_img2.size * 100
    black_pixel2 = np.count_nonzero(diff_img_center2 < 128)
    black_ratio2 = black_pixel2 / diff_img2.size * 100
    os.makedirs('diff/' + sys.argv[1] + '/pre_cleanup', exist_ok=True)
    cv2.imwrite('diff/' + sys.argv[1] + '/pre_cleanup/' + str(n) + '.png', diff_img_center2)

    output_file3 = 'outputs/sampling/clean_line_drawings__pretrain_clean_line_drawings/optimal/png/'\
                   + sys.argv[3] + '/' + str(n) + '.png'
    output_img3 = cv2.imread(output_file3)
    diff_img3 = trace_img.astype(int) - output_img3.astype(int)
    diff_img_center3 = np.floor_divide(diff_img3, 2) + 128
    white_pixel3 = np.count_nonzero(diff_img_center3 > 128)
    white_ratio3 = white_pixel3 / diff_img3.size * 100
    black_pixel3 = np.count_nonzero(diff_img_center3 < 128)
    black_ratio3 = black_pixel3 / diff_img3.size * 100
    os.makedirs('diff/' + sys.argv[1] + '/pre_cleanup_opti', exist_ok=True)
    cv2.imwrite('diff/' + sys.argv[1] + '/pre_cleanup_opti/' + str(n) + '.png', diff_img_center3)

    data.append([n, white_ratio + black_ratio, white_ratio, black_ratio,
                 white_ratio2 + black_ratio2, white_ratio2, black_ratio2,
                 white_ratio3 + black_ratio3, white_ratio3, black_ratio3])

with open('diff/' + sys.argv[1] + '/' + sys.argv[1] + '.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data)