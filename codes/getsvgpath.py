#import io
#import svgelements
#import document
from xml.dom import minidom
import re
from svg.path import parse_path
#https://living-sun.com/ja/python/728928-parsing-svg-file-paths-with-python-python-svg.html
#from bs4 import BeautifulSoup

def get_svg_path(svgfile):
    path_data = []  # ストローク(ベジェ曲線)の座標(始点x,始点y,制御点x,制御点y,終点x,終点y)
    width_data = []  # ストロークの太さ
    svg_dom = minidom.parse(svgfile)
    path_strings = [path.getAttribute("d") for path in svg_dom.getElementsByTagName("path")]  # svgからベジェ曲線のpath取得
    path_data_strings = []
    for path_string in path_strings:  # ベジェ曲線のpathを不要な文字列を除いてstring型にする
        p_s = re.sub(' ', '', path_string)
        p_s = p_s.strip('M')
        path_data_strings.append(re.split('[Q,]', p_s))

    for l in range(len(path_data_strings)):  # float型に変換して挿入
        path_data.append([])
        for p_s_d in path_data_strings[l]:
            path_data[l].append(float(p_s_d))
    #print(len(path_data))
    #print(path_data)

    width_strings = [path.getAttribute("stroke-width") for path in
                     svg_dom.getElementsByTagName("path")]  # svgからpathの太さ取得

    for width_string in width_strings:  # float型に変換して挿入
        width_data.append(float(width_string))
    #print(len(width_data))
    #print(width_data)

    return path_data,width_data