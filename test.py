import cv2 as cv
import numpy as np 
import pytesseract

if __name__ == '__main__':
    CONFIG = '--psm 6 digits'
    pytesseract.pytesseract.tesseract_cmd = r'E:\Fisiere\code\Useful\pytesseract\tesseract.exe'
    img = cv.imread('images/char.png')
    a = pytesseract.image_to_string(img, config=CONFIG)
    a.replace('\f','')
    print(int(a[0])) 