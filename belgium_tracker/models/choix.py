# coding: utf-8
from odoo import models, fields


class Choix(models.Model):
    _name = 'belgium_tracker.choix'

    vote_id = fields.Many2one('belgium_tracker.vote', required=True, index=True)
    depute_id = fields.Many2one('belgium_tracker.depute', required=True, index=True)
    parti_id = fields.Many2one('belgium_tracker.parti', index=True)
    choix = fields.Selection([('pour', 'Pour'),
                              ('contre', 'Contre'),
                              ('abs', 'Abstention')])

    # TODO au create/write, le parti doit être recopié du député
