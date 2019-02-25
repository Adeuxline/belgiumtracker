# coding: utf-8
from odoo import api, models, fields


class Programme(models.Model):
    _name = 'belgium_tracker.programme'
    _rec_name = 'titre'
    _inherit = ['mail.thread']

    titre = fields.Char('Titre', required=True)
    parti_id = fields.Many2one('belgium_tracker.parti', index=True, required=True)
    proposition_ids = fields.One2many('belgium_tracker.proposition', 'programme_id')


class Proposition(models.Model):
    _name = 'belgium_tracker.proposition'
    _rec_name = 'titre'
    _inherit = ['mail.thread']

    titre = fields.Char('Titre', required=True)
    description = fields.Html()
    programme_id = fields.Many2one('belgium_tracker.programme', index=True, required=True)
    parti_id = fields.Many2one('belgium_tracker.parti', related='programme_id.parti_id')
    tags_ids = fields.Many2many('belgium_tracker.programme_tag')


class ProgrammeTag(models.Model):
    _name = 'belgium_tracker.programme_tag'

    name = fields.Char('Nom', required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]
