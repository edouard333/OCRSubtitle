# L'application ne fonctionne que pour des sous-titres blancs pour l'instant.

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
import numpy as np
import numpy.linalg as LA
import SRTFormat as srt

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


import os.path

# Chemin d'où se trouve tesseract.exe (Windows).
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

# Valeur du texte des sous-titres:
rgb= [180, 180, 180]

# Longueur de la séquence a analuser:
duree_image= 127996

# Fonction qui compare deux chaines de caractères.
def comparaison(texte1, texte2):
    train_set = [texte1]  # Documents
    test_set =  [texte2]  # Query
    stopWords = stopwords.words('French') #english / French

    vectorizer = CountVectorizer(stop_words = stopWords)
    transformer = TfidfTransformer()

    trainVectorizerArray = vectorizer.fit_transform(train_set).toarray()
    testVectorizerArray = vectorizer.transform(test_set).toarray()
    transformer.fit(trainVectorizerArray)
    resultat1= transformer.transform(trainVectorizerArray).toarray()

    # print resultat1

    transformer.fit(testVectorizerArray)
    tfidf = transformer.transform(testVectorizerArray)
    resultat2= tfidf.todense()

    # print resultat2

    resultat= np.subtract(resultat1, resultat2)
    return resultat.sum()

def deuxDigite(valeur):
    if(valeur < 10):
        return '0'+str(valeur)
    else:
        return str(valeur)

def timecode(tc, fr= 25):
    heure= tc/(60*60*fr)
    reste_h= tc%(60*60*fr)
    
    minute= reste_h/(60*fr)
    reste_m= reste_h%(60*fr)
    
    seconde= reste_m/(fr)
    reste_s= reste_m%(fr)
    
    image= reste_s
    return deuxDigite(heure)+':'+deuxDigite(minute)+':'+deuxDigite(seconde)+':'+deuxDigite(image)

# Corrige certains caractère récurent comme souci:
def correctionCaractere(sous_titre):

    if("i|" in sous_titre):
        sous_titre= sous_titre.replace("i|", "il")

    if("éu" in sous_titre):
        sous_titre= sous_titre.replace("éu", "eu")

    if("l/" in sous_titre):
        sous_titre= sous_titre.replace("l/", "v")

    if("||" in sous_titre):
        sous_titre= sous_titre.replace("||", "ll")

    if("§u" in sous_titre):
        sous_titre= sous_titre.replace("§u", "tu")

    if("c§" in sous_titre):
        sous_titre= sous_titre.replace("c§", "o")
    
    return sous_titre

# Corrige certains mot:
def correctionMot(mot):
    switcher={
        "sévoir": "savoir",
        "iT'es": "T'es",
        "ga?": "ça?",
        "denguﬂil/ant.": "de survivant.",
        "Tuicommences": "Tu commences",
        "ime": "me",
        "6‘:": "à",
    }
    return switcher.get(mot, mot)

# Passe dans un filtre corrigant les sous-titres:
def correctionSousTitre(sous_titre):
    sous_titre= correctionCaractere(sous_titre)
    liste_mot= sous_titre.split() # décompose la phrase en mot.
    
    sous_titre= '';

    # Analyse chaque mot:
    for i in range(0, len(liste_mot)):
        if(i != 0):
            sous_titre+= ' '
        sous_titre+= correctionMot(liste_mot[i])
    
    return sous_titre

def PixelModifier(rgb):
    if( (rgb[0]+rgb[1]+rgb[2]) > 180*3 ):
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

# == Le programme: ==

# Le fichier qui récupère les sous-titres.
f = open("fichier_le-depart.srt", "w")
texte_precedent= ''
tc_in= 0

# Numéro de sous-titre:
j= 0

for i in range(0, 127996):

    if(os.path.isfile('_OUTPUT_LeDepart_Python/' + str(i) + '.png')):
        image= Image.open('_OUTPUT_LeDepart_Python/' + str(i) + '.png') #str(i).zfill(5)
    
    # -- Si la valeur est supérieur à 230, alors on a un sous-titre --
    #if(np.amax(image) > 180):

        # On tente de conserver que les sous-titres:
        image = Couche(image)
    
        texte= pytesseract.image_to_string(image, lang='fra').encode('utf-8')

        # Si le texte est différent de rien:
        if(texte != ''):
            try:
                # On ne tient pas compte du 1er sous-titre:
                if(j != 0):
                    coefficient= comparaison(texte, texte_precedent)

                    len0= (float)(len(texte_precedent))
                    len1= (float)(len(texte))

                    # Différence de moins de 25%, alors on considère le coefficient comme devant être précis.
                    if(abs(len0-len1) <= (len1/4)):
                        tolerant= False
                    # Différence de plus de 25% (en longeur de chaine de caractère):
                    else:
                        tolerant= True
                    
                    # le coefficient de similitude doit être comparé à la longueur des deux chaine de caractère:
                    # Si vraiment différente, la comparaison n'a pas de sens.
                    # Si les deux chaines de caractères sont très grande = marge d'erreur peut être plus grande pour dire qu'elles soient identique.
                    # Si les deux chaines de caractères sont très petite = marge d'erreur doit être faible pour dire qu'elles soient identique.
                    if((coefficient > 1.5 and not tolerant) or (coefficient > 1.1 and tolerant)):
                        coef_tolerance= 1.0/abs(len1-len0-1.1)
                        #if(coefficient > 1.5*coef_tolerance):
                        print timecode(i)+'/127996'
                        #print timecode(i) + ' [New:' + str(coefficient) + '/coef_tolerance: ' + str(coef_tolerance) + '] ' + correctionSousTitre(texte)
                        # TODO: le TC out est le prochain sous-titre, donc il faut arrêter ce TC dès que le coéficient est faible!
                        if(texte_precedent != ''):
                            f.write(srt.sous_titre(j, timecode(tc_in), timecode(i), correctionSousTitre(texte_precedent)))

                        # Pour le nouveau sous-titre:
                        texte_precedent= texte
                        tc_in= i
                        j= j+1
                    # Ici = similaire:
                    else:
                        #print timecode(i) + ' [Error] ' + texte
                        a= 1
                else:
                    print timecode(i) + ' [First] ' + correctionSousTitre(texte)
                    tc_in= i
                    texte_precedent= texte
                    j= j+1
                
            except ValueError:
                a= 0

        # Ici si sous-titre fini (prochain = '')...
        elif(texte_precedent != ''):
            corSt= correctionSousTitre(texte_precedent)
            print timecode(i) + ' [end] ' + corSt
            f.write(srt.sous_titre(j, timecode(tc_in), timecode(i), corSt))
            tc_in= i
            #j= j+1
            # Empêche qu'on écrive plusieurs fois le même sous-titre.
            texte_precedent= ''

    elif(texte_precedent != ''):
        corSt= correctionSousTitre(texte_precedent)
        print timecode(i) + ' [end] ' + corSt
        f.write(srt.sous_titre(j, timecode(tc_in), timecode(i), corSt))
        tc_in= i
        #j= j+1
        # Empêche qu'on écrive plusieurs fois le même sous-titre.
        texte_precedent= ''

f.close()
