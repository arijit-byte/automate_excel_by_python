import pytesseract
import cv2
import re
import numpy as np
import os
import pandas as pd
from openpyxl.drawing.image import Image
from openpyxl_image_loader import SheetImageLoader
from openpyxl import workbook, load_workbook
pytesseract.pytesseract.tesseract_cmd=r'C:\ocr_proj_new\ocr_pack\tesseract.exe'

#-------------------------OCR PART
img_ocr = cv2.imread("tcs.png")
#---------P_1------------
# norm_img = np.zeros((img_ocr.shape[0], img_ocr.shape[1]))
# img = cv2.normalize(img_ocr, norm_img, 0, 255, cv2.NORM_MINMAX)
# img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]
# img = cv2.GaussianBlur(img, (1, 1), 0)
#----------P_2-----------
# img = cv2.resize(img_ocr, None, fx=0.5, fy = 0.5)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# thres_var = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 91)
#---------------------

# text = pytesseract.image_to_string(image=img_ocr , lang='eng' ,config='--psm 1 --oem 1')  # -> all good except wipro not comming

# text = pytesseract.image_to_string(image=img_ocr , lang='eng' ,config='--psm 13 --oem 1')  # only wipro is goodall other are bads
text = pytesseract.image_to_string(image=img_ocr , lang='eng')

text_splited = text.split('\n')  # Return splited texts in list
text_joined = " ".join(text_splited)
res = re.sub(' +', ' ', text_joined)

print(res)
