# coding: utf-8
from odoo import http
from odoo.http import request


class VotesController(http.Controller):

    @http.route(['/deputes'], type='http', auth='public', website=True)
    def deputes(self, **kwargs):
        deputes = request.env['belgium_tracker.depute'].search([])
        # TODO search last legislature only
        # last_legislature = request.env['belgium_tracker.legislature'].search([], limit=1)
        return request.render('belgium_tracker.deputes', {'deputes': deputes})

    @http.route(['/depute/<model("belgium_tracker.depute"):depute>'], type='http', auth='public', website=True)
    def depute(self, depute, **kwargs):
        choix = request.env['belgium_tracker.choix'].search([('depute_id', '=', depute.id)])
        return request.render('belgium_tracker.depute', {'depute': depute, 'choix': choix})

    @http.route(['/seances'], type='http', auth='public', website=True)
    def seances(self, **kwargs):
        seances = request.env['belgium_tracker.seance'].search([])
        return request.render('belgium_tracker.seances', {'seances': seances})

    @http.route(['/seance/<model("belgium_tracker.seance"):seance>'], type='http', auth='public', website=True)
    def seance(self, seance, **kwargs):
        return request.render('belgium_tracker.seance', {'seance': seance})

    @http.route(['/vote/<model("belgium_tracker.vote"):vote>'], type='http', auth='public', website=True)
    def vote(self, vote, **kwargs):
        return request.render('belgium_tracker.vote', {'vote': vote})
