# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class snippet_mcm(models.Model):
#     _name = 'snippet_mcm.snippet_mcm'
#     _description = 'snippet_mcm.snippet_mcm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
