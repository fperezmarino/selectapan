# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_family_code(models.Model):
    _name = "medical.family_code"
    _description = "Medical Family Code"

    name = fields.Char(string="Name", required=True)
    operational_sector_id = fields.Many2one('medical.operational_sector', string="Operational Sector")
    members_ids = fields.Many2many('res.partner',string="Members")
    info = fields.Text(string="Extra info")
    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: