# coding: utf-8
from odoo import models, fields


class Legislature(models.Model):
    _name = 'belgium_tracker.legislature'
    _order = 'numero desc'
    _rec_name = 'numero'

    numero = fields.Integer(required=True)
    debut = fields.Date(required=True)
    fin = fields.Date()
