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

# Chemin d'où se trouve tesseract.exe (Windows).
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

# Fonction qui compare deux chaines de caractères.
def comparaison(texte1, texte2):
    train_set = [texte1]  # Documents
    test_set =  [texte2]  # Query
    stopWords = stopwords.words('english') #english / French

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

# TODO: utiliser une fonction toute faite python dans string:
def structure(i):
    if(i < 10):
        return '000' + str(i)
    elif(i < 100):
        return '00' + str(i)
    elif(i < 1000):
        return '0' + str(i)
    else:
        return str(i)

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

# == Le programme: ==

# Le fichier qui récupère les sous-titres.
f = open("fichier.srt", "w")
texte_precedent= ''
tc_in= 0

# Numéro de sous-titre:
j= 1

for i in range(0, 2229):
    image= Image.open('_OUTPUT/LUKAS_ST' + structure(i) + '_T.png')
    
    # -- détecter ici si l'image contient un sous-titre (valeur pixel) --
    
    texte= pytesseract.image_to_string(image, lang='fra').encode('utf-8')

    # Si le texte est différent de rien:
    if(texte != ''):
        try:
            # On ne tient pas compte du 1er sous-titre:
            if(j != 1):
                coefficient= comparaison(texte, texte_precedent)
                if(coefficient > 1.2):
                    print timecode(i) + ' [New:' + str(coefficient) + '] ' + texte
                    # TODO: le TC out est le prochain sous-titre, donc il faut arrêter ce TC dès que le coéficient est faible!
                    if(texte_precedent != ''):
                        f.write(srt.sous_titre(j, timecode(tc_in), timecode(i), texte_precedent))

                    # Pour le nouveau sous-titre:
                    texte_precedent= texte
                    tc_in= i
                    j= j+1
                # Ici = similaire:
                else:
                    #print timecode(i) + ' [Error] ' + texte
                    a= 1
            else:
                print timecode(i) + ' [First] ' + texte
                tc_in= i
                texte_precedent= texte
                j= j+1
            
        except ValueError:
            a= 0

    # Ici si sous-titre fini (prochain = '')...
    elif(texte_precedent != ''):
        print timecode(i) + ' [end] ' + texte
        f.write(srt.sous_titre(j, timecode(tc_in), timecode(i), texte_precedent))
        tc_in= i
        j= j+1
        # Empêche qu'on écrive plusieurs fois le même sous-titre.
        texte_precedent= ''
    

f.close()
