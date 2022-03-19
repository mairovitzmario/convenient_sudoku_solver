import cv2 as cv
import numpy as np 
import pytesseract
from sqlalchemy import false
    

class ImageMethods():
    #TESSERACT_CONFIG = '--oem 3 --psm 6 outputbase digits'   

    @staticmethod
    def get_shape(contour):                                 
        # RETURNEAZA NUMARUL DE COLTURI
        perimeter = cv.arcLength(contour, True)
        points_number = cv.approxPolyDP(contour, 0.02 * perimeter, True)
        return len(points_number)       


    @staticmethod
    def remove_duplicate_contours(contours, poz):           
        corners = contours[poz]
        corners = corners.tolist()

        xmax, ymax =-1, -1
        xmin, ymin=1000000, 1000000
        for corner in corners:
            if corner[0][1] > xmax:
                xmax = corner[0][1]
            if corner[0][1] < xmin:
                xmin = corner[0][1]
            if corner[0][0] > ymax:
                ymax = corner[0][0]
            if corner[0][0] < ymin:
                ymin = corner[0][0]
        # AXA X -> 1; AXA Y -> 0

        # stanga sus -> xmin, ymin
        # stanga jos -> xmin, ymax
        # dreapta jos -> xmax, ymax
        # dreapta sus -> xmax, ymin
        corners = [xmin, xmax, ymin, ymax] 
        return corners





class Cell():                                           
    # CLASA MENITA PENTRU A TINE DETALIILE IMPORTANTE ALE UNEI CELULE DIN CELE 81
    def __init__(self, xmin, ymin, xmax, ymax, index):
        self.xmin = xmin          # COORDONATA X(MIN)
        self.ymin = ymin          # COORDONATA Y(MIN)
        self.xmax = xmax
        self.ymax = ymax
        self.index = index  # INDEXUL IN VECTORUL DE CONTURURI

    def detect_empty(self, img):
        img = img[self.xmin+2:self.xmax-2, self.ymin+2:self.ymax-2]
        average_value = np.average(img)
        for row in img:
            for color_code in row:
                color_value = color_code[0]
                if color_value < average_value - 0.2*average_value or color_value > average_value + 0.2*average_value:
                    return False
        
        return True