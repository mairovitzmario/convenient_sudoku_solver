import cv2 as cv
import numpy as np 
import pytesseract

num = 22
arr = np.array([[1, 30],
                [4, 40]])

if num not in arr:
    print(True)
else:
    print(False)