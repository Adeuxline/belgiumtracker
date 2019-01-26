from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib

SEANCE = str(264)

url = 'http://www.lachambre.be/doc/PCRI/html/54/ip' + str(SEANCE) + 'x.html'
html_doc = urllib.request.urlopen(url)
soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('body'))
doc = soup.get_text()
doc = doc.replace("\xa0"," ")
doc = doc.splitlines()

def isFill(objet):
    if (objet != "\n" and
        objet != " \n" and
        objet != " " and
        objet != "\t\n"):
        return True
    else:
        return False

def conca(objet):
    i = 0
    lines = []
    taille = len(objet)
    while i < taille:
        if isFill(objet[i]):
            string = objet[i]
            if i + 1 < taille:
                i = i + 1
                while isFill(objet[i]):
                    string = string + " " + objet[i]
                    if i + 1 < taille:
                        i = i + 1
                    else:
                        break
                lines.append(string)
                del string
            else:
                i = i + 1
        else:
            i = i + 1
    return lines

doc = conca(doc)

with open('seance_'+ SEANCE +'.txt', 'w') as f:
    for i in range(0, len(doc)):
        if isFill(doc[i]):
            data = str(doc[i])
            data = ' '.join(data.split())
            data = data + '\n'
            f.write(data)

seance_pleniere, caract, odj, votes = [], [], [], []

data = []
lines = []
with open('seance_' + SEANCE  + '.txt', 'r') as f:
    lines = f.readlines()
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace('\n', '')

# CARACTERISTIQUES DE LA SEANCE []
# 0: Numéro
# 1: date [jour, moment, date_longue, YYYYMMDD]
# 2: liens [pdf, pda, text]
# 3: version provisoire/définitive
# 4: annexe

# CARACTERISTIQUES DE l'ODJ []
# 0: Numéro
# 1: titre NL
# 2: titre FR
# 3: liste des documents associés []

# Pour l'ODJ
for i in range(0, len(lines)):
    agenda = []
    if lines[i][0:1].isdigit() and lines[i][2] == ' ':
        
        numero = str(lines[i][0:2])
        agenda.append(numero)

        spliteur = str(' ') + numero + str(' ')
        # Parfois, nl et fr sont inversés...
        nl, fr = lines[i].split(spliteur, 1)
        poubelle, nl = nl.split(' ',1)
        agenda.append(nl)
        agenda.append(fr)

        # Trouver une reggex pour analyser fr ou nl, et récupérer un string entre () avec un / au milieu. Ca donnera les documents.
        agenda.append('Insérer des documents ici.')

# Pour les votes
temp = []
compteur = 0
t = 0
cancel = 0
for i in range(0, len(lines)):
    temp_vote = []
    if '(Stemming/vote ' in lines[i] or 'Vote/stemming ' in lines[i]:
        if str(lines[i][16]) == ')':
#           print(lines[i][15])
            temp_vote.append(str('00') + str(lines[i][15]))
        else:
#           print(str(lines[i][15]) + str(lines[i][16]))
            temp_vote.append(str('0') + str(lines[i][15]) + lines[i][16])
        t = t + 1
        if 'projet de loi' in lines[i-3] or 'Projet de loi' in lines[i-3]:
#           print('Projet de loi ' + str(i-2))
            compteur = compteur + 1
            temp_vote.append('Projet de loi')
        elif 'proposition de résolution' in lines[i-3] or 'Proposition de résolution' in lines[i-3]:
#           print('Proposition de résolution ' + str(i-2))
            compteur = compteur + 1
            temp_vote.append('Proposition de résolution')
        elif 'proposition de rejet' in lines[i-3] or 'Proposition de rejet' in lines[i-3]:
#           print('Proposition de rejet ' + str(i-2))
            compteur = compteur + 1
            temp_vote.append('Proposition de rejet')
        elif 'proposition de loi' in lines[i-3] or 'Proposition de loi' in lines[i-3]:
#           print('Proposition de loi ' + str(i-2))
            compteur = compteur + 1
            temp_vote.append('Proposition de loi')
        elif 'Stemming over amendement' in lines[i-2][0:24]:
#           print ('Amendement ' + str(i-1))
            compteur = compteur + 1
            temp_vote.append('Amendement')
        elif 'Vote sur l\'amendement' in lines[i-2][0:21]:
#           print('Amendement ' + str(i-1))
            compteur = compteur + 1
            temp_vote.append('Amendement')
        else:
            temp_vote.append('À TROUVER.')
    # Pour les votes qui ont été annulés... Comme le vote 37 dans la séance 264
    elif '(Stemming nr.' in lines[i]:
        temp_vote.append(lines[i][14] + lines[i][15])
        temp_vote.append('À TROUVER')
        cancel = cancel + 1
    if len(temp_vote) > 1:
        temp.append(temp_vote)

# Permet de ne chercher que dans la partie inférieure de la liste, pour éviter d'utiliser trop de mémoire
debut_votes_nominatifs = ''
for i in range(0, len(lines)):
    if lines[i] == 'Détail des votes nominatifs':
        debut_votes_nominatifs = str(i)

#############
#   VOTES   #
#############
# 
# 1. Numéro du vote
# 2. Type de vote (amendement, projet de loi, ... )
# 3. Nombre de oui
# 4. Liste de oui
# 5. Nombre de non
# 6. Liste de non
# 7. Nombre d'abs
# 8. Liste d'abs
#


# Le compteur permet de vérifier qu'on a bien eu tous les votes
compteur = 0
for i in range(0, len(temp)):
    for j in range(int(debut_votes_nominatifs), len(lines)):
        if 'Vote nominatif' in lines[j] and temp[i][0] in lines[j]:
            # le bonus est le nombre de ligne qu'il faut descendre après avoir lu le nombre de votes.
            # Quand le nombre est égal à 000, il n'y a pas de liste de noms, donc il ne faut pas utiliser la ligne suivante
            bonus = 1
            # Oui
            data = lines[j+bonus].split()
            temp[i].append(data[1])
            # liste oui
            if '000' in lines[j+bonus]:
                temp[i].append(' ')
            else:
                bonus = bonus + 1
                data = lines[j+bonus].split(', ')
                temp[i].append(data)
            # Non
            bonus = bonus + 1
            data = lines[j+bonus].split()
            temp[i].append(data[1])
            # liste non
            if '000' in lines[j+bonus]:
                temp[i].append(' ')
            else:
                bonus = bonus + 1
                data = lines[j+bonus].split(', ')
                temp[i].append(data)
            # Abs
            bonus = bonus + 1
            data = lines[j+bonus].split()
            temp[i].append(data[1])
            # liste abs
            if '000' in lines[j+bonus]:
                temp[i].append(' ')
            else:
                bonus = bonus + 1
                data = lines[j+bonus].split(', ')
                temp[i].append(data)

            compteur = compteur + 1
