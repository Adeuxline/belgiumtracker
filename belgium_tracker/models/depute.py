# coding: utf-8
from odoo import api, models, fields


class Depute(models.Model):
    _name = 'belgium_tracker.depute'
    _inherit = ['mail.thread']

    name = fields.Char('Nom complet', compute='_compute_name', store=True, index=True)
    first_name = fields.Char('Prénom', required=True, index=True)
    last_name = fields.Char('Nom', required=True, index=True)
    parti_id = fields.Many2one('belgium_tracker.parti', index=True, track_visibility='onchange')
    # TODO gérer les changements de parti
    date_naissance = fields.Date()
    date_deces = fields.Date()
    email = fields.Char()
    genre = fields.Selection([('m', 'M'), ('f', 'F')])
    langue = fields.Selection([('fr', 'Francophone'), ('nl', 'Néerlandophone')])
    site = fields.Char()
    photo = fields.Binary(attachment=True)

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for depute in self:
            depute.name = ' '.join([depute.first_name, depute.last_name])


class Situation(models.Model):
    _name = 'belgium_tracker.situation'

    depute_id = fields.Many2one('belgium_tracker.depute', required=True)
    date_begin = fields.Date(required=True)
    date_end = fields.Date(required=True)
