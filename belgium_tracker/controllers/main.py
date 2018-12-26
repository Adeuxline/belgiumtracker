# coding: utf-8
from odoo import http
from odoo.http import request


class VotesController(http.Controller):

    @http.route(['/votes'], type='http', auth='public', website=True)
    def events(self):
        deputes = request.env['belgium_tracker.depute'].search([])
        return " ".join([d.name for d in deputes])
