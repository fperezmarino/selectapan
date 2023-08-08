# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _


class Company(models.Model):
    _inherit = "res.company"

    district_id = fields.Many2one("school.district", "District")
    district_ids = fields.Many2many(
        "school.district", string="Districts",
        relation='district_company_rel', column1='company_id', column2='district_id')

    district_school_ids = fields.One2many(
        "school.school", string="District schools",
        related="district_ids.school_ids")

    school_id = fields.Many2one('school.school', string="School")
    school_ids = fields.Many2many(
        'school.school', string="Schools",
        relation='school_company_rel', column1='company_id', column2='school_id')
    district_name = fields.Char(related="district_id.name", string="District name")

    current_school_year_id = fields.Many2one('school.period', string="Current school year")
    enrollment_school_year_id = fields.Many2one('school.period', string="Enrollment school year")

    @api.onchange('district_ids')
    def _onchange_school_ids(self):
        for company in self:
            company.school_ids = company.district_ids.mapped('school_ids')
