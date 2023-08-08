# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SchoolBaseDistrict(models.Model):
    """ Districts """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.district'
    _description = "District"
    _order = "sequence"
    _rec_name = 'display_name'
    _inherit = ['school.mixin.with.code', 'image.mixin']

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    sequence = fields.Integer(default=1)
    school_ids = fields.One2many(
        "school.school", "district_id", string="School")
    company_ids = fields.Many2many(
        "res.company", string="Companies",
        default=lambda self: self.env.companies,
        relation='district_company_rel', column1='district_id', column2='company_id', required=True)
    reference_id = fields.Char('District Reference ID')
    ##############################
    # Compute and search methods #
    ##############################

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
