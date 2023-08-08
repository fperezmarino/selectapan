"""
Created on Feb 18, 2020

@author: LuisMora
"""
from odoo import models, fields


class SchoolBaseMedicalCondition(models.Model):
    _name = 'school.healthcare.condition'
    _description = "Medical condition"

    name = fields.Char("Name")
    comment = fields.Char("Comment")
    
    partner_id = fields.Many2one("res.partner", string="Partner")
