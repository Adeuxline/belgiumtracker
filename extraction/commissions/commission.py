from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib
import re
import json

from functions import *

def create_dic(name):
    return

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
    commission['introduction'] = intro

    # ordre du jour
    commission['odj'] = {}
    commission['reunion'] = {}
    for line in range(line, len(doc)):
        regex = re.compile('^[0-9]{2}\s[A-Z][a-z]+')
        if regex.match(doc[line]):
            point = re.compile('\s[0-9]+\s').split(doc[line])
            pointOdj = point[0][:2]
            commission['odj'][pointOdj] = {}
            commission['odj'][pointOdj]['fr'] = point[0][3:].strip()
            commission['odj'][pointOdj]['nl'] = point[1].strip()
            
            commission['reunion'][pointOdj] = {}
            new_line = line + 1
            new_regex = re.compile('^[0-9]{2}[.][0-9]{2}\s')
            for new_line in range(new_line, len(doc)):
                if new_regex.match(doc[new_line]):
                    
                    souspoint = doc[new_line][3] + doc[new_line][4]
                    commission['reunion'][pointOdj][souspoint] = {}

                    commission['reunion'][pointOdj][souspoint]['intervention'] = doc[new_line][6:].strip()
                    commission['reunion'][pointOdj][souspoint]['intervenant'] = {}
                    
                    intervenant = commission['reunion'][pointOdj][souspoint]['intervention'].split(':')[0].strip()
                    
                    if 'Minister' in intervenant:
                        commission['reunion'][pointOdj][souspoint]['intervenant']['nom'] = intervenant.split(' ', 1)[1].strip()
                        commission['reunion'][pointOdj][souspoint]['intervenant']['statut'] = 'Ministre'
                    elif '(' in intervenant:
                        commission['reunion'][pointOdj][souspoint]['intervenant']['nom'] = intervenant.split('(')[0].strip()
                        commission['reunion'][pointOdj][souspoint]['intervenant']['statut'] = intervenant.split('(')[1].strip().replace(')', '')
                    elif ',' in intervenant:
                        commission['reunion'][pointOdj][souspoint]['intervenant']['nom'] = intervenant.split(',')[0].strip()
                        commission['reunion'][pointOdj][souspoint]['intervenant']['statut'] = 'Ministre'

                    details = []
                    second_line = new_line + 1
                    commission['reunion'][pointOdj][souspoint]['details'] = []
                    for second_line in range(second_line, len(doc)):
                        if new_regex.match(doc[second_line]) or regex.match(doc[second_line]):
                            break
                        else:
                            commission['reunion'][pointOdj][souspoint]['details'].append(doc[second_line].strip())
                    
                
                if regex.match(doc[new_line]):
                    break
    
    return commission

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


