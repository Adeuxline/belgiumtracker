# coding: utf-8
from odoo import api, models, fields


TOTAL_DEPUTES_CHAMBRE = 150


class Vote(models.Model):
    _name = 'belgium_tracker.vote'
    _order = 'seance_id'

    name = fields.Char(required=True)
    seance_id = fields.Many2one('belgium_tracker.seance', required=True, index=True)
    ttype = fields.Selection([('projet', 'Projet de loi'),
                              ('proposition', 'Proposition de loi'),
                              ('amendement', 'Amendement'),
                              ('other', 'Autre')], required=True, index=True)
    description = fields.Html()
    choix_ids = fields.One2many('belgium_tracker.choix', 'vote_id')
    total_oui = fields.Integer(compute='_compute_totaux', store=True)
    total_non = fields.Integer(compute='_compute_totaux', store=True)
    total_abstentions = fields.Integer(compute='_compute_totaux', store=True)
    total_autres = fields.Integer(compute='_compute_totaux', store=True)

    @api.depends('choix_ids.choix')
    def _compute_totaux(self):
        for vote in self:
            liste_choix = vote.choix_ids
            vote.total_oui = len([c for c in liste_choix if c.choix == 'pour'])
            vote.total_non = len([c for c in liste_choix if c.choix == 'contre'])
            vote.total_abstentions = len([c for c in liste_choix if c.choix == 'abs'])
            vote.total_autres = len([c for c in liste_choix if not c.choix])
