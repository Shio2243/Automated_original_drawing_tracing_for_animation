import math
import colorsys
import numpy as np

class FindOptimalSolution:
    def __init__(self, imageLoc, hsv):
        self.img = imageLoc
        self.img_h, self.img_w, self.ing_c = self.img.shape
        self.value = hsv

    def check_size(self):
        return self.img_h, self.img_w

    def get_value(self, x, y):  # 指定した位置の輝度を求める
        x = int(x)
        y = int(y)
        if x < 0:
            x = 0
        elif x >= self.img_w:
            x = self.img_w - 1
        if y < 0:
            y = 0
        elif y >= self.img_h:
            y = self.img_h - 1
        px = self.img[y, x]
        # print(px)#0=blue,1=green,2=red
        hsv = colorsys.rgb_to_hsv(px[2], px[1], px[0])
        return hsv

    def check_distance(self, x, y):  # 距離チェック
        dist = math.sqrt(x ** 2 + y ** 2)
        return dist

    def check_angle(self, m, cA, cB):
        angle = math.degrees(math.atan2(cA[1] - m[1], cA[0] - m[0]) - math.atan2(cB[1] - m[1], cB[0] - m[0]))
        return abs(angle)

    def check_between_points(self, p1, p2):  # ２つの座標をつなぐ直線上は線の上か
        s = [p2[0] - p1[0], p2[1] - p1[1]]
        for l in range(100):  # 二点間の線の割合を求める
            px_value = self.get_value(int(p1[0] + s[0] * l / 100), int(p1[1] + s[1] * l / 100))
            if px_value >= self.value:  # 線の上にあるのか確認
                return False
        return True

    def check_on_the_path(self, path, n, v):  # nは曲線の分割数,vは許容値
        p1 = [path[0], path[1]]
        p2 = [path[2], path[3]]
        p3 = [path[4], path[5]]
        return self.check_on_the_line(p1, p2, p3, n, v)

    def check_on_the_line(self, p1, p2, p3, n, v):
        out_of_line = 0
        for t in range(n):  # 0 <= t <= 1
            bz_x = (1 - t / n) ** 2 * p1[0] + 2 * (1 - t / n) * t / n * (p2[0]) + (t / n) ** 2 * p3[0]
            bz_y = (1 - t / n) ** 2 * p1[1] + 2 * (1 - t / n) * t / n * (p2[1]) + (t / n) ** 2 * p3[1]
            if bz_x <= 0 or self.img_w <= bz_x or bz_y <= 0 or self.img_h <= bz_y:
                return False
            if bz_x != bz_x or bz_y != bz_y:  # NaNがいないかチェック
                continue
            px_value = self.get_value(bz_x, bz_y)
            if px_value[2] >= self.value:  # 背景上にあるのか確認
                out_of_line += 1
                if out_of_line > v:
                    return False
        return True

    def check_width(self, pointx, pointy, get_point):  # 任意の点の周りの線の幅を求める
        r_data, new_x, new_y = [], [], []
        for r in range(360):
            r_data.append(0)
            new_x.append(0)
            new_y.append(0)
            in_white = False
            while not in_white:
                new_x[r] = int(pointx + r_data[r] * math.cos(math.radians(r)))
                new_y[r] = int(pointy + r_data[r] * math.sin(math.radians(r)))
                if new_x[r] <= 0 or self.img_w <= new_x[r] or new_y[r] <= 0 or self.img_h <= new_y[r]:
                    r_data[r] += 9999
                    in_white = True
                    continue
                px_value = self.get_value(new_x[r], new_y[r])
                if px_value[2] < self.value:
                    r_data[r] += 1
                else:
                    in_white = True
        if get_point:
            return r_data, new_x, new_y
        return r_data

    def pos_adjust(self, pointx, pointy):  # 任意の点の位置を調節する
        init_px_value = self.get_value(int(pointx), int(pointy))
        if init_px_value[2] >= self.value:  # 白地の上にいたら近くの線の上へ移動させる
            s_data = []
            for s in range(360):
                s_data.append(0)
                in_black = False
                while not in_black:
                    new_x = int(pointx + s_data[s] * math.cos(math.radians(s)))
                    new_y = int(pointy + s_data[s] * math.sin(math.radians(s)))
                    if new_x <= 0 or self.img_w <= new_x or new_y <= 0 or self.img_h <= new_y:  # 画像の端についたら終了
                        s_data[s] += 9999
                        in_black = True
                        continue
                    px_value = self.get_value(new_x, new_y)
                    s_data[s] += 1
                    if px_value[2] < self.value:  # 線の上なら終了
                        in_black = True
            min_data = ([i for i, x in enumerate(s_data) if x == min(s_data)])  # 最小のベクトル一覧
            selected_angle = round(sum(min_data) / len(min_data))  # 最小のベクトル平均
            pointx += s_data[selected_angle] * math.cos(math.radians(selected_angle))  # 最小ベクトル追加
            pointy += s_data[selected_angle] * math.sin(math.radians(selected_angle))
        r_data, get_x, get_y = self.check_width(pointx, pointy, True)  # その座標周りの線の幅
        new_x = np.mean(get_x)
        new_y = np.mean(get_y)
        return new_x, new_y

    def width_adjust(self, path_data):  # 太さの調節
        p1 = [path_data[0], path_data[1]]
        p2 = [path_data[2], path_data[3]]
        p3 = [path_data[4], path_data[5]]
        min_width = None
        for t in range(5):  # 0 <= t <= 1
            # 2次ベジェ曲線公式x,y
            bz_x = (1 - t / 4) ** 2 * p1[0] + 2 * (1 - t / 4) * t / 4 * (p2[0]) + (t / 4) ** 2 * p3[0]
            bz_y = (1 - t / 4) ** 2 * p1[1] + 2 * (1 - t / 4) * t / 4 * (p2[1]) + (t / 4) ** 2 * p3[1]
            r_data = self.check_width(bz_x, bz_y, False)
            width_data = []
            for n in range(180):
                width_data.append(r_data[n] + r_data[n + 180])
            if min_width is None or min(width_data) < min_width:
                min_width = min(width_data)
        return min_width

    def con_adjust_2(self, path_data):
        p1 = [path_data[0], path_data[1]]
        p2 = [path_data[2], path_data[3]]
        p3 = [path_data[4], path_data[5]]
        bz_t_min = None
        t_min = None
        bz_x_min = None
        bz_y_min = None
        for t in range(100):  # 0 <= t <= 1
            # 2次ベジェ曲線公式x,y
            bz_x = (1 - t / 100) ** 2 * p1[0] + 2 * (1 - t / 100) * t / 100 * (p2[0]) + (t / 100) ** 2 * p3[0]
            bz_y = (1 - t / 100) ** 2 * p1[1] + 2 * (1 - t / 100) * t / 100 * (p2[1]) + (t / 100) ** 2 * p3[1]
            bz_t = math.sqrt((p2[0] - bz_x) ** 2 + (p2[1] - bz_y) ** 2)  # 制御点との距離
            if bz_t_min is None or bz_t < bz_t_min:  # 曲線上で制御点に最も近い座標を求める
                bz_t_min = bz_t
                t_min = t
                bz_x_min = bz_x
                bz_y_min = bz_y
        bz_x_min, bz_y_min = self.pos_adjust(bz_x_min, bz_y_min)  # 位置調節
        new_p2 = [0, 0]  # 求めた座標を通る制御点を求める
        new_p2[0] = (bz_x_min - (1 - t_min / 100) ** 2 * p1[0] - (t_min / 100) ** 2 * p3[0]) \
                    / (2 * (1 - t_min / 100) * t_min / 100)
        new_p2[1] = (bz_y_min - (1 - t_min / 100) ** 2 * p1[1] - (t_min / 100) ** 2 * p3[1]) \
                    / (2 * (1 - t_min / 100) * t_min / 100)
        return new_p2[0], new_p2[1]

    def adjust_2_Bezier(self, path_data):
        p1 = [path_data[0], path_data[1]]
        p2 = [path_data[2], path_data[3]]
        p3 = [path_data[4], path_data[5]]
        new_p1 = self.pos_adjust(path_data[0], path_data[1])
        fitness1 = self.check_on_the_line(new_p1, p2, p3, 100, 0)  # 曲線と元の画像の線との一致率(始点)
        if fitness1:
            p1 = new_p1
            path_data[0], path_data[1] = new_p1[0], new_p1[1]
        new_p3 = self.pos_adjust(path_data[4], path_data[5])
        fitness3 = self.check_on_the_line(p1, p2, new_p3, 100, 0)  # 曲線と元の画像の線との一致率(終点)
        if fitness3:
            p3 = new_p3
            path_data[4], path_data[5] = new_p3[0], new_p3[1]
        fitness13 = self.check_on_the_line(new_p1, p2, new_p3, 100, 0)  # 曲線と元の画像の線との一致率(終点)
        if fitness13:
            p1 = new_p1
            p3 = new_p3
            path_data[0], path_data[1] = new_p1[0], new_p1[1]
            path_data[4], path_data[5] = new_p3[0], new_p3[1]
        new_p2 = self.con_adjust_2(path_data)
        fitness2 = self.check_on_the_line(p1, new_p2, p3, 100, 5)  # 曲線と元の画像の線との一致率(制御点)
        if fitness2:
            path_data[2], path_data[3] = new_p2[0], new_p2[1]
        fitness123 = self.check_on_the_line(new_p1, new_p2, new_p3, 100, 5)  # 曲線と元の画像の線との一致率(制御点)
        if fitness123:
            path_data[0], path_data[1] = new_p1[0], new_p1[1]
            path_data[2], path_data[3] = new_p2[0], new_p2[1]
            path_data[4], path_data[5] = new_p3[0], new_p3[1]
        new_path_data = [path_data[0], path_data[1], path_data[2], path_data[3], path_data[4], path_data[5]]
        return new_path_data

    def make_2_Bezier(self, path_data, width_data, num):
        path_string = '\n  <path d="M ' + str(path_data[0]) + ', ' + str(path_data[1]) \
                      + ' Q ' + str(path_data[2]) + ', ' + str(path_data[3]) + ', ' \
                      + str(path_data[4]) + ', ' + str(path_data[5]) + ' " fill="none" id="curve_' + str(num) \
                      + '" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="' \
                      + str(width_data) + '"/>'
        return path_string
