import sys                      # System bindings
import cv2                      # OpenCV bindings
import numpy as np
import colorsys# add
from collections import Counter
#https://ichi.pro/opencv-to-python-o-shiyoshita-haikeishoku-no-kenshutsu-38403556356675

class BackgroundColorDetector():
    def __init__(self, imageLoc):
        self.img = cv2.imread(imageLoc, 1)
        self.manual_count = {}
        self.w, self.h, self.channels = self.img.shape
        self.total_pixels = self.w*self.h

    def count(self):
        for y in range(0, self.h):
            for x in range(0, self.w):
                RGB = (self.img[x, y, 2], self.img[x, y, 1], self.img[x, y, 0])
                if RGB in self.manual_count:
                    self.manual_count[RGB] += 1
                else:
                    self.manual_count[RGB] = 1

    def average_colour(self):
        red = 0
        green = 0
        blue = 0
        sample = 10
        for top in range(0, sample):
            red += self.number_counter[top][0][0]
            green += self.number_counter[top][0][1]
            blue += self.number_counter[top][0][2]

        average_red = red / sample
        average_green = green / sample
        average_blue = blue / sample
        #print("Average RGB for top ten is: (", average_red,
        #      ", ", average_green, ", ", average_blue, ")")
        return (average_red, average_green, average_blue)

    def twenty_most_common(self):
        self.count()
        self.number_counter = Counter(self.manual_count).most_common(20)
        #for rgb, value in self.number_counter:
        #    print(rgb, value, ((float(value)/self.total_pixels)*100))

    def detect(self):
        self.twenty_most_common()
        self.percentage_of_first = (
            float(self.number_counter[0][1])/self.total_pixels)
        print(self.percentage_of_first)
        viewRGB = 0
        if self.percentage_of_first > 0.5:
            #print("Background color is ", self.number_counter[0][0])
            viewRGB = self.number_counter[0][0]
        else:
            viewRGB = self.average_colour()
        HSV = colorsys.rgb_to_hsv(viewRGB[2], viewRGB[1], viewRGB[0])  # HSVに変換
        return HSV  # HSVを返す