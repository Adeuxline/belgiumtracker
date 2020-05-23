# coding: utf-8
import json

from odoo import api, models, fields


TOTAL_DEPUTES_CHAMBRE = 150


class Vote(models.Model):
    _name = 'belgium_tracker.vote'
    _order = 'seance_id'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    seance_id = fields.Many2one('belgium_tracker.seance', required=True, index=True)
    ttype = fields.Selection([('projet', 'Projet de loi'),
                              ('proposition', 'Proposition de loi'),
                              ('proposition_resolution', 'Proposition de résolution'),
                              ('proposition_rejet', 'Proposition de rejet'),
                              ('amendement', 'Amendement'),
                              ('other', 'Autre')], required=True, index=True)
    description = fields.Html()
    choix_ids = fields.One2many('belgium_tracker.choix', 'vote_id')
    total_oui = fields.Integer(compute='_compute_totaux', store=True)
    total_non = fields.Integer(compute='_compute_totaux', store=True)
    total_abstentions = fields.Integer(compute='_compute_totaux', store=True)
    total_autres = fields.Integer(compute='_compute_totaux', store=True)
    tags_ids = fields.Many2many('belgium_tracker.programme_tag')

    json_data = fields.Char(compute='_compute_json_data')

    @api.depends('choix_ids.choix')
    def _compute_totaux(self):
        for vote in self:
            liste_choix = vote.choix_ids
            vote.total_oui = len([c for c in liste_choix if c.choix == 'pour'])
            vote.total_non = len([c for c in liste_choix if c.choix == 'contre'])
            vote.total_abstentions = len([c for c in liste_choix if c.choix == 'abs'])
            vote.total_autres = len([c for c in liste_choix if not c.choix])

    @api.depends('total_oui', 'total_non', 'total_abstentions')
    def _compute_json_data(self):
        for vote in self:
            vote.json_data = json.dumps([{"label": "Oui", "value": self.total_oui},
                                         {"label": "Non", "value": self.total_non},
                                         {"label": "Abstentions", "value": self.total_abstentions}
                                         ])
