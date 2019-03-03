# coding: utf-8
from bs4 import BeautifulSoup, SoupStrainer
from csv import DictReader
from io import StringIO
from pprint import PrettyPrinter
from urllib import request

from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.addons.belgium_tracker.util import tools


class WizardImportSeance(models.TransientModel):
    _name = 'belgium_tracker.wizard_import_seance'

    legislature_id = fields.Many2one('belgium_tracker.legislature', required=True)
    seance_limit_no = fields.Integer("Don't import seances strictly before no ")

    def action_scrape(self):
        csv_data = StringIO()
        self._scrape_to_file(csv_data, self.legislature_id.numero)
        csv_data.seek(0)
        Seance = self.env['belgium_tracker.seance']
        Attachment = self.env['ir.attachment']
        for row in DictReader(csv_data):
            if self.seance_limit_no and int(row['name']) < self.seance_limit_no:
                continue
            else:
                seance_id = Seance.create({'name': row['name'],
                                           'legislature_id': self.legislature_id.id,
                                           'date': row['date'],
                                           'moment': row['moment'],
                                           'approuve': True if row['approuve'] == 'true' else False})
                if seance_id:

                    # helper
                    def _create_attachment(name, url):
                        Attachment.create({'name': name,
                                           'url': url,
                                           'type': 'url',
                                           'res_model': 'belgium_tracker.seance',
                                           'res_id': seance_id.id,
                                           'public': True})
                    # helper

                    if row['pdf']:
                        _create_attachment('compte rendu imprimable', row['pdf'])
                    if row['pda']:
                        _create_attachment('compte rendu structure', row['pda'])
                    if row['text']:
                        _create_attachment('compte rendu texte', row['text'])
                    if row['annexe']:
                        _create_attachment('annexe', row['annexe'])
        csv_data.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _scrape_to_file(self, doc, legislature_no):
        # Nombre de séances plénières à afficher. S'il faut les afficher toutes,
        # retirer l'attribut 'limit' dans la première boucle for
        NB_MAX = 1000

        # Récupération du code source de la page
        url = 'http://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=plen&cricra=cri&count=all&legislat=%s' % legislature_no
        html_doc = request.urlopen(url)

        soup = BeautifulSoup(html_doc, 'lxml')
        doc.write('name,legislature,date,moment,pdf,pda,text,approuve,annexe' + '\n')
        for link in soup.find_all('tr', valign='top', limit=NB_MAX):
            record = ''
            # Numéro de la séance
            for line in link.find_all('td', height="25px", limit=1):
                for data in line.find_all('a'):
                    record = record + data.string + ','
            # Numéro de la législature
            record = '%s%s,' % (record, legislature_no)
            # Récupération de la date: JJ mois YYYY
            for line in link.find_all('td', style='line-height: 1.0em;', width='110px', limit=1):
                line = " ".join(line.string.split())
                jour, mois, annee = line.split(' ', 2)
                jour = '{0:02d}'.format(int(jour))  # les jours doivent toujours faire 2 caractères: ex 02
                record = record + annee + tools.month_fr_to_numbers(mois) + jour + ','

            # Récupération du jour et du moment de la journée (AM, PM, Soir)
            for line in link.find_all('i', style='font-size: 1.0em;color: 999999;', limit=1):
                line = " ".join(line.string.split())
                try:
                    jour, moment = line.split(' ', 1)
                except ValueError:
                    jour = 'jour'
                    moment = 'journee'
                record = record + moment.lower() + ','

            # Récupération du lien pour le pdf structuré, la brochure bilingue et le contenu en html
            pdf, pda, text = '', '', ''
            for line in link.find_all('a', title='La brochure imprim?e', limit=1):
                pdf = 'http://www.lachambre.be' + line.get('href')
            for line in link.find_all('a', title='PDF structuré', limit=1):
                pda = 'http://www.lachambre.be' + line.get('href')
            for line in link.find_all('a', title='Version HTML prête à copier', limit=1):
                text = 'http://www.lachambre.be' + line.get('href')
            record = record + ('%s,%s,%s,' % (pdf, pda, text))

            # Récupération du statut du PV de la séance (approuvé ou pas)
            for line in link.find_all('i', style='font-size: 0.9em;color: 999999;', limit=1):
                line = " ".join(line.string.split())
                if line == 'version définitive':
                    approuve = 'true,'
                else:
                    approuve = 'false,'
                record = record + approuve

            # Vérifie s'il y a une annexe ou pas. Si oui, donne le lien. Sinon, n'affiche rien.
            # limit=4 parce le style est le même que pour les 3 documents
            # pdf/pda/text et que je ne veux que l'annexe.
            annexe = ''
            for line in link.find_all('td', style='line-height: 1.0em;', width='70px', limit=4):
                for data in line.find_all('a'):
                    if data.string == 'Annexe':
                        annexe = 'http://www.lachambre.be' + data.get('href')
            record = record + annexe

            doc.write(record + '\n')


class WizardImportVote(models.TransientModel):
    _name = 'belgium_tracker.wizard_import_vote'

    seance_id = fields.Many2one('belgium_tracker.seance', required=True, default=lambda s: s._context.get('active_id', False))

    def action_scrape(self):
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'belgium_tracker.seance'), ('res_id', '=', self.seance_id.id), ('name', '=', 'compte rendu texte')], limit=1)
        if not attachment:
            raise ValidationError("""Il n'y a pas de pièce-jointe nommée "compte rendu texte" pour cette séance.""")
        url = attachment.url
        html_doc = request.urlopen(url)
        soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('body'))
        doc = soup.get_text()
        doc = doc.replace("\xa0", " ")
        doc = doc.splitlines()

        def isFill(objet):
            if (objet != "\n" and objet != " \n" and objet != " " and objet != "\t\n"):
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

        lines = []
        for l in doc:
            if isFill(l):
                data = ' '.join(l.split())
                lines.append(data.strip())

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
                poubelle, nl = nl.split(' ', 1)
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
                    temp_vote.append(str('00') + str(lines[i][15]))
                else:
                    temp_vote.append(str('0') + str(lines[i][15]) + lines[i][16])
                t = t + 1
                if 'projet de loi' in lines[i - 3] or 'Projet de loi' in lines[i - 3]:
                    compteur = compteur + 1
                    temp_vote.append('Projet de loi')
                elif 'proposition de résolution' in lines[i - 3] or 'Proposition de résolution' in lines[i - 3]:
                    compteur = compteur + 1
                    temp_vote.append('Proposition de résolution')
                elif 'proposition de rejet' in lines[i - 3] or 'Proposition de rejet' in lines[i - 3]:
                    compteur = compteur + 1
                    temp_vote.append('Proposition de rejet')
                elif 'proposition de loi' in lines[i - 3] or 'Proposition de loi' in lines[i - 3]:
                    compteur = compteur + 1
                    temp_vote.append('Proposition de loi')
                elif 'Stemming over amendement' in lines[i - 2][0:24]:
                    compteur = compteur + 1
                    temp_vote.append('Amendement')
                elif 'Vote sur l\'amendement' in lines[i - 2][0:21]:
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
        data = []
        for i in range(0, len(temp)):
            for j in range(int(debut_votes_nominatifs), len(lines)):
                if 'Vote nominatif' in lines[j] and temp[i][0] in lines[j]:
                    # le bonus est le nombre de ligne qu'il faut descendre après avoir lu le nombre de votes.
                    # Quand le nombre est égal à 000, il n'y a pas de liste de noms, donc il ne faut pas utiliser la ligne suivante
                    bonus = 1
                    # Oui
                    data = lines[j + bonus].split()
                    temp[i].append(data[1])
                    # liste oui
                    if '000' in lines[j + bonus]:
                        temp[i].append(' ')
                    else:
                        bonus = bonus + 1
                        data = lines[j + bonus].split(', ')
                        temp[i].append(data)
                    # Non
                    bonus = bonus + 1
                    data = lines[j + bonus].split()
                    temp[i].append(data[1])
                    # liste non
                    if '000' in lines[j + bonus]:
                        temp[i].append(' ')
                    else:
                        bonus = bonus + 1
                        data = lines[j + bonus].split(', ')
                        temp[i].append(data)
                    # Abs
                    bonus = bonus + 1
                    data = lines[j + bonus].split()
                    temp[i].append(data[1])
                    # liste abs
                    if '000' in lines[j + bonus]:
                        temp[i].append(' ')
                    else:
                        bonus = bonus + 1
                        data = lines[j + bonus].split(', ')
                        temp[i].append(data)

                    compteur = compteur + 1

        # TODO here create votes from data
        # TODO fix this
        for vote in temp:
            body = PrettyPrinter().pformat(vote)
            self.seance_id.message_post(body=body)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
