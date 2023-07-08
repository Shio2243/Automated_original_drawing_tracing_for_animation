import tkinter as tk  # ウィンドウ作成用
from tkinter import filedialog  # ファイルを開くダイアログ用
from PIL import Image, ImageTk, ImageOps  # 画像データ用
import cv2  # OpenCV二値画像
import numpy as np  # アフィン変換行列演算用
import os  # ディレクトリ操作用
import time  # 時間計測

import auto_binary

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.start_time = None  # 前処理開始時間
        self.filename = None  # 表示する画像データディレクトリ
        self.pil_image = None  # 表示する画像データ
        self.cv2_image = None  # 編集される画像データ
        self.edit_image = None  # 編集中の画像データ
        self.edited_image = None  # 編集された画像データ
        self.line_image = None  # 線だけの画像データ
        self.old_x = None
        self.old_y = None
        self.R_left_top = [0, 0]  # 左上座標
        self.R_right_bottom = [0, 0]  # 右下座標
        self.R_range = 0  # +四角の大きさ
        self.b_var = 128
        self.m_var = 1
        self.p_var = 1
        self.pre_b_var = None
        self.pre_m_var = None
        self.erase_mode = True
        self.check_value = tk.BooleanVar(value=True)
        self.my_title = "Get_outline_Window"  # タイトル
        self.back_color = "#888888"  # 背景色

        # ウィンドウの設定
        self.master.title(self.my_title)  # タイトル
        self.master.geometry("600x600")  # サイズ
        self.paned_window = tk.PanedWindow(self.master, orient=tk.VERTICAL)
        self.tool_window = tk.Frame(self.paned_window, height=50)
        self.image_window = tk.Frame(self.paned_window, height=550)
        self.paned_window.add(self.tool_window)
        self.paned_window.add(self.image_window)
        self.create_menu()  # メニューの作成
        self.create_toolbar()  # ツールバーの作成
        self.create_widget()  # ウィジェットの作成
        self.paned_window.pack(expand=True, fill=tk.BOTH)

    def menu_open_clicked(self, event=None):
        # ファイル→開く
        self.filename = tk.filedialog.askopenfilename(
            filetypes=[("Image file", ".png .jpg .JPG .bmp .tif"), ("PNG", ".png"), ("JPEG", ".jpg .JPG"),
                       ("Bitmap", ".bmp"), ("Tiff", ".tif")],  # ファイルフィルタ
            initialdir=os.getcwd()  # カレントディレクトリ
        )
        # 画像ファイルを設定する
        self.set_image(self.filename)

        # 画像ファイルの読み込み
        if self.filename:
            self.start_time = time.perf_counter()  # 計測開始
            self.cv2_image = cv2.imread(self.filename, cv2.IMREAD_GRAYSCALE)
            self.b_var, self.m_var = auto_binary.get_binary_kernel(self.filename)  # 閾値,カーネルサイズ取得
            self.ScaleB.set(self.b_var)
            self.ScaleM.set(self.m_var)
            self.menu_edit_clicked()
            save_file = os.path.splitext(os.path.basename(self.filename))[0] + \
                            "_m" + str(self.pre_m_var) + "b" + str(self.pre_b_var) + ".png"
            cv2.imwrite(save_file, self.edited_image)
            # 終了時刻
            end_time = time.perf_counter()
            # 差を出力
            processing_time = end_time - self.start_time
            print("自動処理processing_time: " + str(processing_time) + "\n")


    def menu_save_clicked(self, event=None):  # +画像の保存
        if not self.filename:
            return
        end_time = time.perf_counter()
        # 差を出力
        processing_time = end_time - self.start_time
        print("編集込みprocessing_time: " + str(processing_time) + "\n")
        save_img_name = os.path.splitext(os.path.basename(self.filename))[0] + \
                        "_m" + str(self.pre_m_var) + "b" + str(self.pre_b_var)
        save_file = filedialog.asksaveasfilename(
            title="名前を付けて保存",
            filetypes=[("Image file", ".png .jpg .JPG .bmp .tif"), ("PNG", ".png"), ("JPEG", ".jpg .JPG"),
                       ("Bitmap", ".bmp"), ("Tiff", ".tif")],  # ファイルフィルタ
            initialdir=os.getcwd(),  # カレントディレクトリ
            initialfile=save_img_name,
            defaultextension=".png"
        )
        if not save_file:
            return
        #save_image = Image.fromarray(self.edited_image)
        #save_image.save(save_file)
        cv2.imwrite(save_file, self.edited_image)

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy()

    # create_menuメソッドを定義

    def get_view_image(self, event=None):  # 画像の表示の仕方
        if self.edited_image is None:
            return
        if self.check_value.get():
            self.pil_image = Image.fromarray(self.cv2_image)  # 元の画像
            self.line_image = ImageOps.invert(Image.fromarray(self.edited_image))  # 反転
            black_image = Image.new("L", (self.pil_image.width, self.pil_image.height))  # 黒の画像
            self.pil_image.paste(black_image, (0, 0), self.line_image)  # 元の画像に生成された線だけを合成
        else :
            self.pil_image = Image.fromarray(self.edited_image)
        self.draw_image(self.pil_image)

    def check_reverse(self, event=None):
        # チェックの状態を取得し逆に設定する
        value = self.check_value.get()
        self.check_value.set(not value)
        self.get_view_image()

    def menu_edit_clicked(self, event=None):  # +画像の閾値処理
        if self.cv2_image is None:
            return
        self.edit_image = self.cv2_image
        self.pre_b_var = self.b_var
        self.pre_m_var = self.m_var
        if self.m_var is not 1:
            self.edit_image = cv2.medianBlur(self.edit_image, self.m_var)
        ret, self.edit_image = cv2.threshold(self.edit_image, self.b_var, 255, cv2.THRESH_BINARY)
        self.edited_image = self.edit_image.copy()  # 二値化処理された画像
        self.get_view_image()
        # 画像全体に表示するようにアフィン変換行列を設定
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # 画像の表示
        self.draw_image(self.pil_image)

    def menu_add_clicked(self, event=None):
        if self.cv2_image is None:
            return
        self.edit_image = self.cv2_image
        if self.R_range is not 0:
            Left, Top = self.get_image_point(self.R_left_top[0], self.R_left_top[1])
            Right, Bottom = self.get_image_point(self.R_right_bottom[0], self.R_right_bottom[1])
            if Left < 0: Left = 0
            if Top < 0: Top = 0
            if Right > self.pil_image.width: Right = self.pil_image.width
            if Bottom > self.pil_image.height: Bottom = self.pil_image.height
            self.edit_image = self.edit_image[Top: Bottom, Left: Right]
            if self.m_var is not 1:
                self.edit_image = cv2.medianBlur(self.edit_image, self.m_var)
            ret, self.edit_image = cv2.threshold(self.edit_image, self.b_var, 255, cv2.THRESH_BINARY)
            if self.edited_image is None:
                self.edited_image = self.cv2_image
            self.edited_image[Top: Bottom, Left: Right] = self.edit_image
            self.get_view_image()

    def white_wash(self, event=None):
        if self.cv2_image is None:
            return
        if self.R_range is not 0:
            Left, Top = self.get_image_point(self.R_left_top[0], self.R_left_top[1])
            Right, Bottom = self.get_image_point(self.R_right_bottom[0], self.R_right_bottom[1])
            if Left < 0: Left = 0
            if Top < 0: Top = 0
            if Right > self.pil_image.width: Right = self.pil_image.width
            if Bottom > self.pil_image.height: Bottom = self.pil_image.height
            if self.edited_image is None:
                self.edited_image = self.cv2_image
            cv2.rectangle(self.edited_image, (Left, Top), (Right, Bottom), (255, 255, 255), thickness=-1)
            self.get_view_image()

    def menu_reset_clicked(self, event=None):  # +表示する画像の初期化
        # 画像ファイルを設定する
        self.set_image(self.filename)
        self.start_time = time.perf_counter()

    def create_menu(self):
        self.menu_bar = tk.Menu(self)  # Menuクラスからmenu_barインスタンスを生成

        self.file_menu = tk.Menu(self.menu_bar, tearoff=tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command=self.menu_open_clicked, accelerator="Ctrl+F")
        self.file_menu.add_command(label="Save", command=self.menu_save_clicked, accelerator="Ctrl+S")
        self.file_menu.add_separator()  # セパレーターを追加
        self.file_menu.add_command(label="Exit", command=self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-f>", self.menu_open_clicked)  # ファイルを開くのショートカット(Ctrl+Fボタン)
        self.menu_bar.bind_all("<Control-s>", self.menu_save_clicked)  # 画像保存のショートカット(Ctrl+Sボタン)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=tk.OFF)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Binary", command=self.menu_edit_clicked, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="White", command=self.white_wash, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Add", command=self.menu_add_clicked, accelerator="Ctrl+A")
        self.edit_menu.add_separator()  # セパレーターを追加
        self.edit_menu.add_command(label="Reset", command=self.menu_reset_clicked, accelerator="Ctrl+R")

        self.menu_bar.bind_all("<Control-z>", self.menu_edit_clicked)  # 閾値処理のショートカット(Ctrl+Zボタン)
        self.menu_bar.bind_all("<Control-x>", self.white_wash)  # 白塗りつぶしのショートカット(Ctrl+Xボタン)
        self.menu_bar.bind_all("<Control-a>", self.menu_add_clicked)  # 範囲指定閾値処理のショートカット(Ctrl+Aボタン)
        self.menu_bar.bind_all("<Control-c>", self.check_reverse)  # 表示方法切り替えのショートカット(Ctrl+Cボタン)
        self.menu_bar.bind_all("<Control-d>", self.mode_change)  # 表示方法切り替えのショートカット(Ctrl+dボタン)
        self.menu_bar.bind_all("<Control-r>", self.menu_reset_clicked)  # 画像のリセットのショートカット(Ctrl+Rボタン)

        self.master.config(menu=self.menu_bar)  # メニューバーの配置

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.tool_window)

        self.labelB = tk.Label(self.toolbar, text='Binary')
        self.labelB.pack(side=tk.LEFT)
        self.scaleB_var = tk.IntVar()
        self.ScaleB = tk.Scale(self.toolbar, variable=self.scaleB_var, command=self.slider_scroll, orient=tk.HORIZONTAL,
                               length=150, width=20, sliderlength=20, from_=0, to=255, tickinterval=51)
        self.ScaleB.pack(side=tk.LEFT)
        self.ScaleB.set(self.b_var)

        self.labelM = tk.Label(self.toolbar, text='Median')
        self.labelM.pack(side=tk.LEFT)
        self.scaleM_var = tk.IntVar()
        self.ScaleM = tk.Scale(self.toolbar, variable=self.scaleM_var, command=self.slider_scroll, orient=tk.HORIZONTAL,
                               length=50, width=20, sliderlength=10, from_=1, to=21, resolution=2, tickinterval=10)
        self.ScaleM.pack(side=tk.LEFT)

        self.labelP = tk.Label(self.toolbar, text='Pen')
        self.labelP.pack(side=tk.LEFT)
        self.scaleP_var = tk.IntVar()
        self.ScaleP = tk.Scale(self.toolbar, variable=self.scaleP_var, command=self.slider_scroll, orient=tk.HORIZONTAL,
                               length=100, width=20, sliderlength=10, from_=1, to=100, tickinterval=49)
        self.ScaleP.pack(side=tk.LEFT)

        self.textP = tk.StringVar()
        self.textP.set("Erase")
        self.ButtonP = tk.Button(self.toolbar, textvariable=self.textP, command=self.mode_change)
        self.ButtonP.pack(side=tk.LEFT)

        self.CheckB = tk.Checkbutton(self.toolbar, text="Compare", variable=self.check_value, command=self.get_view_image)
        self.CheckB.pack(side=tk.LEFT)

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def slider_scroll(self, event=None):
        """スライダーを移動したとき"""
        self.b_var = self.scaleB_var.get()
        self.m_var = self.scaleM_var.get()
        self.p_var = self.scaleP_var.get()
        self.var_changed = True

    def mode_change(self, event=None):
        if self.erase_mode is True:
            self.erase_mode = False
            self.textP.set("Draw")
        else:
            self.erase_mode = True
            self.textP.set("Erase")

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
        self.canvas = tk.Canvas(self.image_window, background=self.back_color)
        self.canvas.pack(expand=True, fill=tk.BOTH)  # この両方でDock.Fillと同じ

        # マウスイベント
        self.canvas.bind("<Motion>", self.mouse_move)  # MouseMove
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)  # MouseMove（左ボタンを押しながら移動）
        self.canvas.bind("<Button-1>", self.mouse_down_left)  # MouseDown（左ボタン）
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left)  # MouseDoubleClick（左ボタン）
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release_left)  # MouseRelease（左ボタン）
        self.canvas.bind("<B3-Motion>", self.mouse_move_right)  # MouseMove（右ボタンを押しながら移動）
        self.canvas.bind("<Button-3>", self.mouse_down_right)  # MouseDown（右ボタン）
        self.canvas.bind("<Double-Button-3>", self.mouse_double_click_right)  # MouseDoubleClick（右ボタン）
        self.canvas.bind("<ButtonRelease-3>", self.mouse_release_right)  # MouseRelease（右ボタン）
        # self.canvas.bind("<MouseWheel>", self.mouse_wheel)  # MouseWheel
        self.canvas.bind("<Button-2>", self.mouse_down_Wheel)  # MouseWheelDown（ホイールボタン）
        self.canvas.bind("<ButtonRelease-2>", self.mouse_release_Wheel)  # MouseWheelRelease（ホイールボタン）
        self.canvas.bind("<ButtonPress-4>", self.mouse_wheel_up)  # MouseWheel（linuxアップ）
        self.canvas.bind("<ButtonPress-5>", self.mouse_wheel_down)  # MouseWheel（linuxダウン）

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

        self.pre_b_var = None
        self.pre_m_var = None

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

    def mouse_down_left(self, event):
        pass

    def mouse_move_left(self, event):
        if self.edited_image is None:
            return
        x, y = self.get_image_point(event.x, event.y)
        if self.old_x and self.old_y:
            color = (0, 0, 0)
            if self.erase_mode is True:
                color = (255, 255, 255)
            self.edited_image = cv2.line(self.edited_image, (self.old_x, self.old_y), (x, y),
                                         color, thickness=self.p_var)
            self.get_view_image()
        self.old_x = x
        self.old_y = y

    def mouse_release_left(self, event):
        self.old_x = None
        self.old_y = None
        self.var_changed = False

    def mouse_double_click_left(self, event):
        # self.mode_change()
        pass

    def mouse_down_Wheel(self, event):  # 赤四角描画始点
        ''' マウスのホイールを押した '''
        self.R_left_top = [event.x, event.y]

    def mouse_release_Wheel(self, event):  # 赤四角描画
        ''' マウスのホイールを離した '''
        self.R_right_bottom = [event.x, event.y]
        for i in range(2):
            if self.R_left_top[i] > self.R_right_bottom[i]:
                self.R_left_top[i], self.R_right_bottom[i] = self.R_right_bottom[i], self.R_left_top[i]
        self.R_range = (self.R_left_top[0] - self.R_right_bottom[0]) * (self.R_left_top[1] - self.R_right_bottom[1])
        self.redraw_image()

    def mouse_move_right(self, event):  # 画面移動
        ''' マウスの右クリックをドラッグ '''
        if self.var_changed is True:
            return
        if self.pil_image == None:
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()  # 再描画
        self.__old_event = event

    def mouse_down_right(self, event):
        ''' マウスの右クリックを押した '''
        self.__old_event = event

    def mouse_double_click_right(self, event):  # 画像を画面中央に表示
        ''' マウスの右クリックをダブルクリック '''
        if self.var_changed is True:
            return
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()  # 再描画

    def mouse_release_right(self, event):
        self.var_changed = False

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
