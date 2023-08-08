# -*- coding: utf-8 -*-
# from odoo import http


# class DollarRate(http.Controller):
#     @http.route('/dollar_rate/dollar_rate', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dollar_rate/dollar_rate/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dollar_rate.listing', {
#             'root': '/dollar_rate/dollar_rate',
#             'objects': http.request.env['dollar_rate.dollar_rate'].search([]),
#         })

#     @http.route('/dollar_rate/dollar_rate/objects/<model("dollar_rate.dollar_rate"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dollar_rate.object', {
#             'object': obj
#         })
