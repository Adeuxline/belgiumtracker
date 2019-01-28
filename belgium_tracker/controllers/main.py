# coding: utf-8
from odoo import http
from odoo.http import request


class VotesController(http.Controller):

    @http.route(['/mps'], type='http', auth='public', website=True)
    def mps(self):
        deputes = request.env['belgium_tracker.depute'].search([])
        # TODO search last legislature only
        # FIXME make it reachable by public users
        return request.render('belgium_tracker.deputes', {'deputes': deputes})

    @http.route(['/mp/<model("belgium_tracker.depute"):depute>'], type='http', auth='public', website=True)
    def depute(self, depute):
        return request.render('belgium_tracker.depute', {'depute': depute})

    @http.route(['/seances'], type='http', auth='public', website=True)
    def seances(self):
        seances = request.env['belgium_tracker.seance'].search([])
        # FIXME make it reachable by public users
        return request.render('belgium_tracker.seances', {'seances': seances})

    @http.route(['/seance/<model("belgium_tracker.seance"):seance>'], type='http', auth='public', website=True)
    def seance(self, seance):
        return request.render('belgium_tracker.seance', {'seance': seance})

    @http.route(['/vote/<model("belgium_tracker.vote"):vote>'], type='http', auth='public', website=True)
    def vote(self, vote):
        return request.render('belgium_tracker.vote', {'vote': vote})
