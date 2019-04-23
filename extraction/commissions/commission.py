from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib
import re

from functions import *

def full(doc):
    commission = {}
    line = 0
    compteur = 0
    
    # données inutiles
    for line in range(0, len(doc)):
        if doc[line] == '______':
            compteur = compteur + 1
        if doc[line] == '______' and compteur == 2:
            line = line + 2
            break
    
    # intro avant les différents points de l'ordre du jour
    intro = []
    for line in range(line, len(doc)):
        regex = re.compile('^[0-9]{2}\s[A-Z][a-z]+') 
        if regex.match(doc[line]):
            break
        else:
            intro.append(doc[line].strip())
    commission["introduction"] = intro

    # ordre du jour : uniquement les points principaux. Pour voir les détails, voir "reunion"
    commission["odj"] = {}
    commission["reunion"] = {}
    for line in range(line, len(doc)):
        # recherche des lignes commençant ayant en début de phrase deux ciffres, un espace, une majuscule et une suite de minuscules
        # EXEMPLE : "01 Charles"
        regex = re.compile('^[0-9]{2}\s[A-Z][a-z]+')
        if regex.match(doc[line]):
            # coupe en deux le point de l'odre du jour grâce au numéro au milieu de la ligne qui permet de voir quand commence la traduction du point
            # EXEMPLE : " 01 " ou " 123 "
            point = re.compile('\s[0-9]+\s').split(doc[line])
            # récupère le numero du point de l'odj
            pointOdj = point[0][:2]
            commission["odj"][pointOdj] = {}
            # récupère la première phrase du point (fr/nl... On ne sait pas) en retirant son numéro
            commission["odj"][pointOdj]["fr"] = point[0][3:].strip()
            # récupère la deuxième phrase du point
            commission["odj"][pointOdj]["nl"] = point[1].strip()
            
            commission["reunion"][pointOdj] = {}

            # recherche des sous-points dans le PV
            new_line = line + 1
            # recherche des lignes ayant en début de phrase deux chiffres, un point, deux chiffres, un espace
            # EXEMPLE : "01.04 "
            new_regex = re.compile('^[0-9]{2}[.][0-9]{2}\s')
            for new_line in range(new_line, len(doc)):
                if new_regex.match(doc[new_line]):
                    
                    # dans "01.04", le souspoint correspond à "04"
                    souspoint = doc[new_line][3] + doc[new_line][4]
                    commission["reunion"][pointOdj][souspoint] = {}

                    # la première ligne du souspoint est l'intervention
                    commission["reunion"][pointOdj][souspoint]["intervention"] = doc[new_line][6:].strip()
                    commission["reunion"][pointOdj][souspoint]["intervenant"] = {}
                    
                    # Une intervention commence toujours par "Nom Prenom (parti):" ou par "Nom Prenom, minisre:". On récupère donc ce qu'il y a avant les ":"
                    intervenant = commission["reunion"][pointOdj][souspoint]["intervention"].split(':')[0].strip()
                    
                    # Version NL, le "Minister" vient devant le nom et prénom
                    if 'Minister' in intervenant:
                        # on coupe en deux sur le premier espace et on récupère la deuxième partie
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["nom"] = intervenant.split(' ', 1)[1].strip()
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["statut"] = 'Ministre'
                    elif '(' in intervenant:
                        # on coupe en deux sur "(", et on récupère la première partie pour le nom, la deuxième partie pour le parti
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["nom"] = intervenant.split('(')[0].strip()
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["statut"] = intervenant.split('(')[1].strip().replace(')', '')
                    elif ',' in intervenant:
                        # on coupe en deux sur "," et on récupère la première partie pour le nom. Le statut est "Ministre" d'office. Version FR de la première condition
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["nom"] = intervenant.split(',')[0].strip()
                        commission["reunion"][pointOdj][souspoint]["intervenant"]["statut"] = 'Ministre'

                    # Récupération de la suite des lignes concernant l'intervention
                    details = []
                    second_line = new_line + 1
                    commission["reunion"][pointOdj][souspoint]["details"] = []
                    for second_line in range(second_line, len(doc)):
                        # si la ligne corresponf à un souspoint ou à un point de l'odj, on s'arrête. Sinon, on récupère la ligne.
                        if new_regex.match(doc[second_line]) or regex.match(doc[second_line]):
                            break
                        else:
                            commission["reunion"][pointOdj][souspoint]["details"].append(doc[second_line].strip())
                    
                # si la ligne correspond à un point de l'odre du jour, on s'arrête
                if regex.match(doc[new_line]):
                    break
    
    return commission

# récupération du document en ligne et préparation de ce dernier pour utilisation
def init(commission):
    url = 'http://www.lachambre.be/doc/CCRI/html/54/ic' + str(commission) + 'x.html'
    html_doc = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('body'))
    doc = soup.get_text()
    doc = doc.replace("\xa0"," ")
    doc = doc.splitlines()
    doc = conca(doc)
    create_file(doc, commission)

    return doc


def main():
    
    numero = str(1070)
    doc = []
    doc = init(numero)
    commission = full(doc)

# main()

numero = str(1070)
doc = []
doc = init(numero)
commission = full(doc)


