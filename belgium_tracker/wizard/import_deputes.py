# coding: utf-8
from base64 import b64encode
from bs4 import BeautifulSoup
from csv import DictReader
from io import StringIO
from urllib import request

from odoo import models, fields
from odoo.addons.belgium_tracker.util import tools


NB_DEPUTE = 150
URL = 'http://www.lachambre.be/kvvcr/showpage.cfm?section=/depute&language=fr&cfm=cvlist54.cfm?legis=54&today=y'


class WizardImportDepute(models.TransientModel):
    _name = 'belgium_tracker.wizard_import_depute'

    # currently used for display only, to avoid security issues
    page_url = fields.Char(required=True, readonly=True, default=lambda x: URL)

    def action_scrape(self):
        # TODO avoid to create duplicate deputes :D

        csv_data = StringIO()
        self._scrape_to_file(csv_data, URL)
        # assure que tous les partis existent en db
        csv_data.seek(0)
        partis_names = set()
        partis_ids = {}
        for row in DictReader(csv_data):
            partis_names.add(row['parti_id'])
        Parti = self.env['belgium_tracker.parti']
        for p in partis_names:
            res = Parti.search([('sigle', 'ilike', p)], limit=1)
            if res:
                partis_ids[p] = res.id
            else:
                partis_ids[p] = Parti.name_create(p)[0]
        # cree les deputes
        csv_data.seek(0)
        for row in DictReader(csv_data):
            # convert pic to base 64
            pic_data = b64encode(request.urlopen(row['photo']).read())
            self.env['belgium_tracker.depute'].create({'first_name': row['last_name'],
                                                       'last_name': row['first_name'],
                                                       'langue': row['langue'],
                                                       'genre': row['genre'],
                                                       # FIXME Gros hack pourri
                                                       'date_naissance': row['date_naissance'] if row['first_name'] != 'Luykx' else False,
                                                       'email': row['email'],
                                                       'site': row['site'],
                                                       'parti_id': partis_ids[row['parti_id']],
                                                       'photo': pic_data,
                                                       })
        csv_data.close()

    def _scrape_to_file(self, doc, url):
        html_doc = request.urlopen(url)
        niveau_max = BeautifulSoup(html_doc, 'lxml')

        # fichier = 'deputes' + '.csv'
        # doc = open(fichier, 'w')
        doc.write('name,first_name,last_name,photo,langue,genre,date_naissance,parti_id,email,site,date_deces' + '\n')

        # Fouille les données de la page du député
        def page_depute(url):
            code_html = request.urlopen(url)
            code_depute = BeautifulSoup(code_html, 'lxml')

            # Pour trouver la photo
            for niveau_0 in code_depute.find_all('img', border='1', alt='Picture'):
                picture = 'http://www.lachambre.be' + niveau_0.get('src')

            picture = str(picture) + ','

            # Pour trouver la langue du député
            i = 0
            for niveau_0 in code_depute.find_all('td'):
                i = i + 1
                if i == 2:
                    for niveau_1 in niveau_0.find_all('p'):
                        for child in niveau_1.children:
                            child = str(child).split()
                            if 'Néerlandais' in child:
                                langue = 'nl'
                            elif 'Français' in child:
                                langue = 'fr'
                            else:
                                langue = 'Pas de langue.'
            langue = langue + ','

            # Pour trouver la description
            for niveau_0 in code_depute.find_all('tr', valign='top', align='left'):
                for niveau_1 in niveau_0.find_all('td'):
                    for niveau_2 in niveau_1.find_all('p'):
                        niveau_2 = ' '.join(niveau_2.string.split())
            # Pour trouver le sexe
                        if 'Née' in niveau_2:
                            sexe = 'f' + ','
                        else:
                            sexe = 'm' + ','

            # Pour trouver la date de naissance
                        description = niveau_2.split('|')

                        for x in description:
                            if 'Né' in x:
                                data = ' '.join(x.split())
                                data = data.split(' ')
                                data = data[-3:]
                                data[2] = data[2][:4]
                                if data[1][:2] == 'ao' and data[1][3] == 't':
                                    data[1] = 'août'
                                data[1] = tools.month_fr_to_numbers(data[1])
                                if data[0] == '1er':
                                    data[0] = '1'
                                if data[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                    data[0] = str('0') + str(data[0])
                                naissance = str(data[2]) + str(data[1]) + str(data[0])
                                naissance = naissance + ','

            return picture, langue, sexe, naissance

        for niveau_0 in niveau_max.find_all('tr', limit=NB_DEPUTE):
            url_depute = ' '
            # line = ''
            i = 1
            for niveau_1 in niveau_0.find_all('td'):
                if i == 1:
                    i = i + 1
                    for niveau_2 in niveau_1.find_all('a', limit=1):
                        url_depute = str('http://www.lachambre.be/kvvcr/') + str(niveau_2.get('href'))
                        text = niveau_2.find('b').string
                        name = " ".join(text.string.split())
                        name = str(name) + ','
                        doc.write(name)

                        # Séparer les noms et prénoms
                        name = ''.join(reversed(name))
                        last_name, first_name = name.split(' ', 1)

                        first_name = ''.join(reversed(first_name))
                        first_name = str(first_name) + ','
                        doc.write(first_name)

                        last_name = ''.join(reversed(last_name))
                        last_name = str(last_name)
                        doc.write(last_name)

                        picture, langue, sexe, naissance = page_depute(url_depute)

                        doc.write(picture)
                        doc.write(langue)
                        doc.write(sexe)
                        doc.write(naissance)

                elif i == 2:
                    i = i + 1
                    parti_id = niveau_1.find('a').string
                    parti_id = str(" ".join(parti_id.string.split()))
                    if parti_id == 'CD&V;':
                        parti_id = 'CD&V'
                    if parti_id == 'Vuye&Wouters;':
                        parti_id = 'Vuye&Wouters'
                    parti_id = str(parti_id) + ','
                    doc.write(parti_id)
                elif i == 3:
                    i = i + 1
                    try:
                        mail = niveau_1.find('a', 'mail').string[::-1]
                        mail = str(mail) + ','
                    except TypeError:
                        text = 'Pas d\'adresse mail'
                        mail = ','
                    doc.write(mail)
                else:
                    try:
                        text = niveau_1.find('a', target='_blank').get('href')
                        site = str(text) + ',' + '\n'
                    except NameError:
                        text = 'Pas de site web'
                        site = '\n'
                    except AttributeError:
                        text = 'Pas de site web'
                        site = '\n'
                    doc.write(site)
            print(first_name, last_name, picture, langue, sexe, naissance, parti_id, mail, site)
        return doc
