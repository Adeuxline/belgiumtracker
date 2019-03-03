# coding: utf-8
from odoo import api, models, fields


class Choix(models.Model):
    _name = 'belgium_tracker.choix'
    _order = 'vote_id DESC, choix DESC'

    display_name = fields.Char(compute='_compute_display_name')
    vote_id = fields.Many2one('belgium_tracker.vote', required=True, index=True, ondelete='cascade')
    depute_id = fields.Many2one('belgium_tracker.depute', required=True, index=True)
    parti_id = fields.Many2one('belgium_tracker.parti', readonly=True, index=True)
    choix = fields.Selection([('pour', 'Pour'),
                              ('contre', 'Contre'),
                              ('abs', 'Abstention')])

    _sql_constraints = [
        ('vote_depute_unique', 'UNIQUE(vote_id,depute_id)', "Un député ne peut voter qu'une fois.")
    ]

    @api.depends('depute_id', 'choix', 'vote_id')
    def _compute_display_name(self):
        for choix in self:
            choix.display_name = "%s %s %s" % (choix.depute_id.display_name, choix.choix, choix.vote_id.display_name)

    @api.model_create_multi
    def create(self, vals_list):
        # copy the party of the deputy at the moment where it is created
        for value in vals_list:
            if 'parti_id' not in value:
                value['parti_id'] = self.env['belgium_tracker.depute'].browse(value['depute_id']).parti_id.id
        res = super(Choix, self).create(vals_list)
        return res
