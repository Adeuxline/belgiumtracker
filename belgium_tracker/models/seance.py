# coding: utf-8
from odoo import api, models, fields


class Seance(models.Model):
    _name = 'belgium_tracker.seance'
    _order = 'date DESC, moment DESC, id DESC'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    legislature_id = fields.Many2one('belgium_tracker.legislature', required=True, index=True, default=lambda self: self.env['belgium_tracker.legislature'].search([('fin', '=', False)], order='numero DESC', limit=1).id)
    date = fields.Date(required=True, default=fields.Date.context_today)
    moment = fields.Selection([('am', 'Matin'), ('pm', 'Après-midi'), ('soir', 'Soir'), ('journee', 'Journée entière')], required=True)
    approuve = fields.Boolean(track_visibility='onchange')
    votes_ids = fields.One2many('belgium_tracker.vote', 'seance_id')

    @api.multi
    def button_display_votes(self):
        self.ensure_one()
        action_dict = self.env.ref('belgium_tracker.action_votes').read()[0]
        action_dict.update(context="{'domain': [('seance_id', '=', %d)], 'default_seance_id': %d}" % (self.id, self.id))
        return action_dict
