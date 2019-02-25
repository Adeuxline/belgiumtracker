# coding: utf-8
from odoo import api, models, fields


class Parti(models.Model):
    _name = 'belgium_tracker.parti'
    _order = 'sigle, name, id'
    _inherit = ['mail.thread']

    name = fields.Char('Nom', required=True)
    sigle = fields.Char(required=True)
    deputes_ids = fields.One2many('belgium_tracker.depute', 'parti_id')

    @api.model
    def name_create(self, name):
        parti = self.create({'name': name, 'sigle': name})
        return parti.name_get()[0]
