import numpy
from scipy import *
from PIL import Image
from scipy import misc
import cv2

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


def PixelModifier(rgb):
    if( (rgb[0]+rgb[1]+rgb[2]) > 230 ):
        return rgb[0], rgb[1], rgb[2]
    else:
        return 0, 0, 0

def Couche(ImgIn):
    ImgOut= ImgIn.copy()
    width,height = ImgIn.size
    for y in range(1, height - 1): # parcours des pixels en colonne
        for x in range(1, width - 1): # parcours des pixels en ligne
            ImgOut.putpixel((x, y), PixelModifier(ImgOut.getpixel((x, y))))
    return ImgOut

def structure(i):
    if(i < 10):
        return '000' + str(i)
    elif(i < 100):
        return '00' + str(i)
    elif(i < 1000):
        return '0' + str(i)
    else:
        return str(i)

for i in range(0, 2229):
    ImgIn= Image.open('_OUTPUT/LUKAS_ST' + structure(i) + '.png')
    ImgOut = Couche(ImgIn)
    ImgOut.save('_OUTPUT/LUKAS_ST' + structure(i) + '_T.png', format="png")
