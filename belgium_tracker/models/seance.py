# coding: utf-8
from odoo import models, fields


class Seance(models.Model):
    _name = 'belgium_tracker.seance'

    name = fields.Char(required=True)
    date = fields.Date(required=True)
    moment = fields.Selection([('am', 'Matin'), ('pm', 'Après-midi'), ('soir', 'Soir')], required=True)
    approuve = fields.Boolean()
