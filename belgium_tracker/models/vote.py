# coding: utf-8
from odoo import models, fields


class Vote(models.Model):
    _name = 'belgium_tracker.vote'

    name = fields.Char(required=True)
    seance_id = fields.Many2one('belgium_tracker.seance', required=True, index=True)
    ttype = fields.Selection([('projet', 'Projet de loi'),
                              ('proposition', 'Proposition de loi'),
                              ('amendement', 'Amendement'),
                              ('other', 'Autre')], required=True, index=True)
    description = fields.Html()
    deputes_choix_ids = fields.Many2many('belgium_tracker.depute', 'belgium_tracker_choix', 'depute_id', 'vote_id')
