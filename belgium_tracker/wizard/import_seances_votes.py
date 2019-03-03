# coding: utf-8
from bs4 import BeautifulSoup
from csv import DictReader
from io import StringIO
from urllib import request

from odoo import models, fields
from odoo.addons.belgium_tracker.util import tools


class WizardImportSeanceVotes(models.TransientModel):
    _name = 'belgium_tracker.wizard_import_seance_votes'

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
