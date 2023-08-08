# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SchoolBaseSchool(models.Model):
    """ Schools """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.school'
    _description = "School"
    _order = "sequence"
    _inherit = ['school.mixin.with.code', 'image.mixin']
    _rec_name = 'display_name'

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    description = fields.Char("Description")
    sequence = fields.Integer(default=1)
    district_id = fields.Many2one(
        "school.district", "District", required=True, group_expand='_expand_districts')
    program_ids = fields.One2many("school.program", 'school_id')

    district_company_ids = fields.Many2many(
        'res.company', related='district_id.company_ids', string="District companies")
    company_ids = fields.Many2many(
        'res.company', string="Companies",
        relation='school_company_rel', column1='school_id', column2='company_id',
        required=True,
        store=True,
        readonly=False,
        compute='compute_company_ids'
        )
    reference_id = fields.Char('School Reference ID')

    ##############################
    # Compute and search methods #
    ##############################
    def _expand_districts(self, states, domain, order):
        return self.env.companies.district_ids

    @api.depends('district_id', 'district_company_ids')
    def compute_company_ids(self):
        for school in self:
            # We check if the school has some company that isn't in the district's companies
            if not school.company_ids:
                school.company_ids = school.district_company_ids
            elif not all(school.company_ids.mapped(lambda c: c in self.district_company_ids)):
                # We need to remove that company
                companies = school.company_ids.filtered(lambda c: c in self.district_company_ids)
                if not companies:
                    # It is possible that the district code removed all the school companies
                    companies = school.district_company_ids
                school.company_ids = companies



    ###########################
    # Constrains and onchange #
    ###########################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
