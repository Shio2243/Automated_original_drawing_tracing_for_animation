import os
import time
import copy
import tkinter as tk  # ウィンドウ作成用
from tkinter import filedialog  # ファイルを開くダイアログ用
from PIL import Image, ImageTk  # 画像データ用
import cv2  # OpenCV二値画像

import viewcolor
import getsvgpath
import findoptimal
from tools import svg_conversion

import numpy as np
import cairosvg


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.filename = None  # 表示する画像データディレクトリ
        self.pil_image = None  # 表示する画像データ
        self.cv2_image = None  # 編集される画像データ
        self.R_left_top = [0, 0]  # 左上座標
        self.R_right_bottom = [0, 0]  # 右下座標
        self.R_range = 0  # 四角の大きさ
        self.check_value = tk.BooleanVar(value=True)
        self.my_title = "Rewrite_svg_Window"  # タイトル
        self.back_color = "#333333"  # 背景色

        # ウィンドウの設定
        self.master.title(self.my_title)  # タイトル
        self.master.geometry("600x600")  # サイズ

        self.create_menu()  # メニューの作成
        self.create_toolbar()  # +ツールバーの作成
        self.create_widget()  # ウィジェットの作成

    def menu_open_clicked(self, event=None):
        # ファイル→開く
        self.filename = tk.filedialog.askopenfilename(
            filetypes=[("Image file", ".png .jpg .JPG .bmp .tif"), ("PNG", ".png"), ("JPEG", ".jpg .JPG"),
                       ("Bitmap", ".bmp"), ("Tiff", ".tif")],  # ファイルフィルタ
            initialdir=os.getcwd()  # カレントディレクトリ
        )
        # 画像ファイルを設定する
        self.set_image(self.filename)

        # +追加画像ファイルの読み込み
        if self.filename:
            self.cv2_image = cv2.imread(self.filename)

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy()

    def optimizing_img(self, event=None):
        img_name = os.path.splitext(os.path.basename(self.filename))[0]
        img_name = img_name.replace('_input', '')
        basename = os.path.dirname(self.filename) + "/seq_data/" + img_name
        sum_time = 0
        for n in range(10):
            print("----------process" + str(n) + "----------")
            # 開始時刻
            start_time = time.perf_counter()
            svg_conversion.data_convert_to_absolute(basename + "_" + str(n) +".npz", "single")  # svgファイル用意

            made_svg_path = basename + "_" + str(n) + "/single.svg"
            # outputs/sampling/clean_line_drawings__pretrain_clean_line_drawings/seq_data/フォルダ名/single.svg
            path_data = []  # ストローク(ベジェ曲線)の座標(始点x,始点y,制御点x,制御点y,終点x,終点y)
            width_data = []  # ストロークの太さ

            original_img = viewcolor.BackgroundColorDetector(self.filename)
            view_hsv = original_img.detect()  # 元画像の背景色のHSV取得
            path_data, width_data = getsvgpath.get_svg_path(made_svg_path)
            # ------------------------------
            print(view_hsv)
            # print(width_data)
            # Numpy配列に変換
            np_scores = np.array(width_data)
            # numpy.meanで平均値
            mean = np.mean(np_scores)
            print("mean_line_width:" + str(mean))
            # numpy.stdで標準偏差
            std = np.std(np_scores)
            print("Standard_deviation_line_width:" + str(std))
            # ------------------------------
            img_find_optimal = findoptimal.FindOptimalSolution(self.cv2_image, view_hsv[2])
            img_h, img_w = img_find_optimal.check_size()
            svg_len = len(path_data)

            #print('端点・制御点・太さ調節')
            for m in range(svg_len):
                path_data[m] = img_find_optimal.adjust_2_Bezier(path_data[m])
                deviation = (np_scores[m] - mean) / std
                deviation_value = 50 + deviation * 10
                if deviation_value > 90:
                    new_width = img_find_optimal.width_adjust(path_data[m])
                    if new_width > 0:
                        width_data[m] = new_width

            for a in range(svg_len):
                for pA in range(2):
                    maximum_angle = 150  # 最大角度
                    minimum_dist = min([self.pil_image.width, self.pil_image.height]) / 100  # 最小は短辺の100分の1
                    new_a = a
                    new_pa = pA
                    for b in range(svg_len):
                        if a == b:
                            continue
                        for pB in range(2):
                            if (path_data[a][pA * 4] == path_data[b][pB * 4] and
                                    path_data[a][pA * 4 + 1] == path_data[b][pB * 4 + 1]):
                                continue
                            sub_x = path_data[b][pB * 4] - path_data[a][pA * 4]
                            sub_y = path_data[b][pB * 4 + 1] - path_data[a][pA * 4 + 1]
                            dist = img_find_optimal.check_distance(sub_x, sub_y)  # 2点間の距離を求める
                            if dist < minimum_dist:  # 距離が近いとき
                                mid = [(path_data[a][pA * 4] + path_data[b][pB * 4]) / 2,
                                       (path_data[a][pA * 4 + 1] + path_data[b][pB * 4 + 1]) / 2]
                                con_a = [path_data[a][2], path_data[a][3]]
                                con_b = [path_data[b][2], path_data[b][3]]
                                angle = img_find_optimal.check_angle(mid, con_a, con_b)
                                if angle >= maximum_angle:
                                    check_path = copy.copy(path_data[a])
                                    check_path[pA * 4] = copy.copy(path_data[b][pB * 4])  # 点aの座標に点bの座標を代入
                                    check_path[pA * 4 + 1] = copy.copy(path_data[b][pB * 4 + 1])
                                    fitness = img_find_optimal.check_on_the_path(check_path, 100, 0)  # 一致率求める
                                    if fitness:
                                        minimum_dist = dist
                                        maximum_angle = angle
                                        new_a = b
                                        new_pa = pB
                    path_data[a][pA * 4] = copy.copy(path_data[new_a][new_pa * 4])
                    path_data[a][pA * 4 + 1] = copy.copy(path_data[new_a][new_pa * 4 + 1])

            # ここからsvgのテキスト生成
            path_string = '<?xml version="1.0" ?>\n<svg height="' + str(img_h) + '" width="' \
                          + str(img_w) + '" xmlns="http://www.w3.org/2000/svg">'
            path_id = 0
            for l in range(svg_len):
                path_string += img_find_optimal.make_2_Bezier(path_data[l], width_data[l], path_id)
                path_id += 1

            path_string += '\n</svg>'
            os.makedirs('optimal', exist_ok=True)
            svg_file = 'optimal/svg/' + img_name
            png_file = 'optimal/png/' + img_name
            os.makedirs(svg_file, exist_ok=True)
            os.makedirs(png_file, exist_ok=True)
            with open(os.path.join(svg_file, str(n) + '.svg'), mode='w') as f:
                f.write(path_string)
            f.close()
            cairosvg.svg2png(url=svg_file + '/' + str(n) + '.svg', write_to=png_file + '/' + str(n) + '.png')

            # 終了時刻
            end_time = time.perf_counter()
            # 差を出力
            processing_time = end_time - start_time
            print("processing_time: " + str(processing_time) + "\n")
            # 時間加算
            sum_time += processing_time

            value = self.check_value.get()
            if value:
                line_img = cv2.imread(png_file + '/' + str(n) + '.png', cv2.IMREAD_UNCHANGED)
                white_img = np.zeros([self.pil_image.width, self.pil_image.height,3], dtype=np.uint8)
                white_img.fill(255)
                white_img[0:self.pil_image.height, 0:self.pil_image.width] \
                    = white_img[0:self.pil_image.height, 0:self.pil_image.width] \
                      * (1 - line_img[:, :, 3:] / 255) + line_img[:, :, :3] * (line_img[:, :, 3:] / 255)
                cv2.imwrite(png_file + '/' + str(n) + '.png', white_img)

        if value:
            print("背景色あり")
        # 平均時間
        print("average_time: " + str(sum_time / 10))

    def create_menu(self):
        self.menu_bar = tk.Menu(self)  # Menuクラスからmenu_barインスタンスを生成

        self.file_menu = tk.Menu(self.menu_bar, tearoff=tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command=self.menu_open_clicked, accelerator="Ctrl+F")
        self.file_menu.add_command(label="Optimizing", command=self.optimizing_img, accelerator="Ctrl+G")
        self.file_menu.add_command(label="Exit", command=self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-f>", self.menu_open_clicked)  # ファイルを開くのショートカット(Ctrl+Fボタン)
        self.menu_bar.bind_all("<Control-g>", self.optimizing_img)  # 線画修正のショートカット(Ctrl+Gボタン)

        self.master.config(menu=self.menu_bar)  # メニューバーの配置

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.master)
        self.CheckB = tk.Checkbutton(self.toolbar, text="背景を白にする", variable=self.check_value)
        self.CheckB.pack(side=tk.LEFT)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_widget(self):
        """ウィジェットの作成"""

        # ステータスバー相当(親に追加)
        self.statusbar = tk.Frame(self.master)
        self.mouse_position = tk.Label(self.statusbar, relief=tk.SUNKEN, text="mouse position")  # マウスの座標
        self.image_position = tk.Label(self.statusbar, relief=tk.SUNKEN, text="image position")  # 画像の座標
        self.label_space = tk.Label(self.statusbar, relief=tk.SUNKEN)  # 隙間を埋めるだけ
        self.image_info = tk.Label(self.statusbar, relief=tk.SUNKEN, text="image info")  # 画像情報
        self.mouse_position.pack(side=tk.LEFT)
        self.image_position.pack(side=tk.LEFT)
        self.label_space.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.image_info.pack(side=tk.RIGHT)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(self.master, background=self.back_color)
        self.canvas.pack(expand=True, fill=tk.BOTH)  # この両方でDock.Fillと同じ

        # マウスイベント
        self.master.bind("<Motion>", self.mouse_move)  # MouseMove
        self.master.bind("<B1-Motion>", self.mouse_move_left)  # MouseMove（左ボタンを押しながら移動）
        self.master.bind("<Button-1>", self.mouse_down_left)  # MouseDown（左ボタン）
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left)  # MouseDoubleClick（左ボタン）
        self.master.bind("<Button-3>", self.mouse_down_right)  # MouseDown（右ボタン）
        self.master.bind("<ButtonRelease-3>", self.mouse_release_right)  # MouseRelease（右ボタン）
        # self.master.bind("<MouseWheel>", self.mouse_wheel)  # MouseWheel
        self.master.bind("<ButtonPress-4>", self.mouse_wheel_up)  # MouseWheel（linuxアップ）
        self.master.bind("<ButtonPress-5>", self.mouse_wheel_down)  # MouseWheel（linuxダウン）

    def set_image(self, filename):
        ''' 画像ファイルを開く '''
        if not filename:
            return
        # PIL.Imageで開く
        self.pil_image = Image.open(filename)
        # 画像全体に表示するようにアフィン変換行列を設定
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # 画像の表示
        self.draw_image(self.pil_image)

        # ウィンドウタイトルのファイル名を設定
        self.master.title(self.my_title + " - " + os.path.basename(filename))
        # ステータスバーに画像情報を表示する
        self.image_info[
            "text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        # カレントディレクトリの設定
        os.chdir(os.path.dirname(filename))

    # -------------------------------------------------------------------------------
    # マウスイベント
    # -------------------------------------------------------------------------------

    def mouse_move(self, event):
        ''' マウスの移動時 '''
        # マウス座標
        self.mouse_position["text"] = f"mouse(x, y) = ({event.x: 4d}, {event.y: 4d})"

        if self.pil_image == None:
            return

        # 画像座標
        x, y = self.get_image_point(event.x, event.y)
        if x >= 0 and x < self.pil_image.width and y >= 0 and y < self.pil_image.height:
            # 輝度値の取得
            value = self.pil_image.getpixel((x, y))
            self.image_position["text"] = f"image({x: 4d}, {y: 4d}) = {value}"
        else:
            self.image_position["text"] = "-------------------------"

    def mouse_move_left(self, event):
        ''' マウスの左ボタンをドラッグ '''
        if self.pil_image == None:
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()  # 再描画
        self.__old_event = event

    def mouse_down_left(self, event):
        ''' マウスの左ボタンを押した '''
        self.__old_event = event

    def mouse_double_click_left(self, event):
        ''' マウスの左ボタンをダブルクリック '''
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()  # 再描画

    def mouse_down_right(self, event):
        ''' マウスの右ボタンを押した '''
        self.R_left_top = [event.x, event.y]

    def mouse_release_right(self, event):
        ''' マウスの右ボタンを離した '''
        self.R_right_bottom = [event.x, event.y]
        for i in range(2):
            if self.R_left_top[i] > self.R_right_bottom[i]:
                self.R_left_top[i], self.R_right_bottom[i] = self.R_right_bottom[i], self.R_left_top[i]
        self.R_range = (self.R_left_top[0] - self.R_right_bottom[0]) * (self.R_left_top[1] - self.R_right_bottom[1])
        self.redraw_image()

    def mouse_wheel_up(self, event):
        """ マウスホイールを上に回した """
        if self.pil_image is None:
            return
        # 拡大
        self.scale_at(1.25, event.x, event.y)

        self.redraw_image()  # 再描画

    def mouse_wheel_down(self, event):
        """ マウスホイールを下に回した """
        if self.pil_image is None:
            return
        # 縮小
        self.scale_at(0.8, event.x, event.y)

        self.redraw_image()  # 再描画

    # -------------------------------------------------------------------------------
    # 画像表示用アフィン変換
    # -------------------------------------------------------------------------------

    def get_image_point(self, event_x, event_y):
        mouse_posi = np.array([event_x, event_y, 1])  # マウス座標(numpyのベクトル)
        mat_inv = np.linalg.inv(self.mat_affine)  # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
        image_posi = np.dot(mat_inv, mouse_posi)  # 座標のアフィン変換
        x = int(np.floor(image_posi[0]))
        y = int(np.floor(image_posi[1]))
        return x, y

    def reset_transform(self):
        """アフィン変換を初期化（スケール１、移動なし）に戻す"""
        self.mat_affine = np.eye(3)  # 3x3の単位行列

    def translate(self, offset_x, offset_y):
        """ 平行移動 """
        mat = np.eye(3)  # 3x3の単位行列
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale: float):
        """ 拡大縮小 """
        mat = np.eye(3)  # 単位行列
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale: float, cx: float, cy: float):
        """ 座標(cx, cy)を中心に拡大縮小 """

        # 原点へ移動
        self.translate(-cx, -cy)
        # 拡大縮小
        self.scale(scale)
        # 元に戻す
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        """画像をウィジェット全体に表示させる"""

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # アフィン変換の初期化
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            # ウィジェットが横長（画像を縦に合わせる）
            scale = canvas_height / image_height
            # あまり部分の半分を中央に寄せる
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # ウィジェットが縦長（画像を横に合わせる）
            scale = canvas_width / image_width
            # あまり部分の半分を中央に寄せる
            offsety = (canvas_height - image_height * scale) / 2

        # 拡大縮小
        self.scale(scale)
        # あまり部分を中央に寄せる
        self.translate(offsetx, offsety)

    # -------------------------------------------------------------------------------
    # 描画
    # -------------------------------------------------------------------------------

    def draw_rect(self):
        if self.R_range is not 0:
            R_w = self.R_left_top[0] - self.R_right_bottom[0]
            R_h = self.R_left_top[1] - self.R_right_bottom[1]
            R_x = int((self.R_left_top[0] + self.R_right_bottom[0]) / 2)
            R_y = int((self.R_left_top[1] + self.R_right_bottom[1]) / 2)
            self.canvas.create_rectangle(R_x - R_w / 2, R_y - R_h / 2, R_x + R_w / 2, R_y + R_h / 2, outline="red")

    def draw_image(self, pil_image):

        if pil_image == None:
            return

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # キャンバスから画像データへのアフィン変換行列を求める
        # （表示用アフィン変換行列の逆行列を求める）
        mat_inv = np.linalg.inv(self.mat_affine)

        # PILの画像データをアフィン変換する
        dst = pil_image.transform(
            (canvas_width, canvas_height),  # 出力サイズ
            Image.AFFINE,  # アフィン変換
            tuple(mat_inv.flatten()),  # アフィン変換行列（出力→入力への変換行列）を一次元のタプルへ変換
            Image.NEAREST,  # 補間方法、ニアレストネイバー
            fillcolor=self.back_color
        )

        # 表示用画像を保持
        self.image = ImageTk.PhotoImage(image=dst)

        # 画像の描画
        item = self.canvas.create_image(
            0, 0,  # 画像表示位置(左上の座標)
            anchor='nw',  # アンカー、左上が原点
            image=self.image  # 表示画像データ
        )

        self.draw_rect()

    def redraw_image(self):
        ''' 画像の再描画 '''
        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
