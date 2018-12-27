# coding: utf-8
from odoo import models, fields


class Parti(models.Model):
    _name = 'belgium_tracker.parti'
    _order = 'sigle, name, id'

    name = fields.Char('Nom', required=True)
    sigle = fields.Char(required=True)
    deputes_ids = fields.One2many('belgium_tracker.depute', 'parti_id')
