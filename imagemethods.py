import cv2 as cv
import numpy as np 
import pytesseract
    

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
    def __init__(self, x, y, index):
        self.x = x          # COORDONATA X(MIN)
        self.y = y          # COORDONATA Y(MIN)
        self.index = index  # INDEXUL IN VECTORUL DE CONTURURI
