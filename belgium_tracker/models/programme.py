# coding: utf-8
from odoo import api, models, fields
from odoo.exceptions import ValidationError


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
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'display_name'
    _order = 'code, display_name'

    name = fields.Char('Nom', required=True, index=True)
    active = fields.Boolean(default=True)
    code = fields.Char('Code EUROVOC', index=True)
    display_name = fields.Char('Nom complet', compute='_compute_display_name', store=True, index=True)
    parent_id = fields.Many2one('belgium_tracker.programme_tag', 'Tag Parent', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    children_ids = fields.One2many('belgium_tracker.programme_tag', 'parent_id', 'Tags Enfants')
    color = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]

    @api.one
    @api.constrains('parent_id')
    def _check_tag_recursion(self):
        if not self._check_recursion():
            raise ValidationError("Vous ne pouvez pas introduire de boucle dans les tags.")
        return True

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        for tag in self:
            if tag.parent_id:
                tag.display_name = '%s / %s' % (tag.parent_id.display_name, tag.name)
            else:
                tag.display_name = tag.name
