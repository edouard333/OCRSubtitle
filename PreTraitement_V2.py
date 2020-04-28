import numpy as np
import cv2
from PIL import Image

cap = cv2.VideoCapture('depart_Duits_OT.mp4')

# La couleur du sous-titre: on ne code d'image que s'il y a des sous-titres!

# Interval d'où se trouvent les sous-titres dans l'image.
x_min= 40
x_max= 980
y_min= 480
y_max= 530

rgb_valeur= [185,185,185]
tolerance= 35 # Ce qu'on ajoute avant et après la valeur.

# Valeur de la couleur des sous-titres:
rgb_min= [rgb_valeur[0]-tolerance, rgb_valeur[1]-tolerance, rgb_valeur[2]-tolerance]
rgb_max= [rgb_valeur[0]+tolerance, rgb_valeur[1]+tolerance, rgb_valeur[2]+tolerance]

min= np.sum(rgb_min)
#valeur= np.sum(rgb_valeur)
max= np.sum(rgb_max)

i= 0

f = open("_OUTPUT_LeDepart_Python/_liste-plan.txt", "w")
tc_in= -1
tc_out= -1

# On parcoure toute la vidéo:
while(cap.isOpened()):
    # On lit l'image suivante (où la 1ère).
    ret, frame = cap.read()

    if(frame is null):
        break

    # Interval où sont les sous-titres
    frame= frame[y_min:y_max:1, x_min:x_max:1]

    # On selectionne que dans les couleurs des sous-titres:
    frame= np.where(frame > (min/3), frame, 0)
    frame= np.where(frame < (max/3), frame, 0)

    # Il faut au minimum 150 pixels de sous-titre:
    if(frame.sum() > (min/3)*150):
        img= Image.fromarray(frame)
        #img= img.convert("RGBA")
        #img.save("total.png", "png", bits=32)
        img.save('_OUTPUT_LeDepart_Python/' + str(i) + '.png', format= "png")

        if(i != tc_in+1):

            if(tc_out != -1):
                print ' ' + str(tc_out)
                f.write(' ' + str(tc_out)+'\n')
                tc_out= -1
            elif(tc_in != -1):
                print ''
                f.write('\n')

            print str(i),
            f.write(str(i))
            tc_in= i
        else:
             #f.write(' ' + str(i)+'\n')
            tc_in= i
            tc_out= i
        #break

    i= i+1

f.close()
cap.release()
