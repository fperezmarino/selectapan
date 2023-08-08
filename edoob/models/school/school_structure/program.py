# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.fields import Command


class Program(models.Model):
    """ Program """
    ######################
    # Private Attributes #
    ######################
    _name = 'school.program'
    _description = "School program"
    _inherit = ['school.mixin.with.code']
    _rec_name = 'name'

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    full_path_name = fields.Char('Full path name', compute='_compute_full_path_name')
    school_id = fields.Many2one('school.school', group_expand='_expand_schools', required=True)
    school_district_id = fields.Many2one('school.district', related='school_id.district_id', store=True)

    period_ids = fields.One2many('school.period', 'program_id')

    grade_level_ids = fields.One2many('school.grade.level', 'program_id')
    parent_id = fields.Many2one('school.program')
    child_ids = fields.One2many('school.program', 'parent_id')
    reference_id = fields.Char('Program Reference ID')

    ##################
    # Compute method #
    ##################
    def _expand_schools(self, states, domain, order):
        company_ids = self.env.companies
        return company_ids.district_ids.school_ids

    def get_with_parent(self):
        programs = self
        for program in self:
            if program.parent_id:
                parent_programs = program.parent_id.get_with_parent()
                for parent_program in parent_programs:
                    if parent_program not in programs:
                        programs += parent_programs
        return programs

    def _get_program_recursive_parent_name(self):
        self.ensure_one()
        name = "%s / %s / %s" % (self.school_id.district_id.name, self.school_id.name, self.name)
        if self.parent_id:
            name = "%s / %s" % (self.parent_id._get_program_recursive_parent_name(), name)

        return name

    def _compute_full_path_name(self):
        for program in self:
            program.full_path_name = program._get_program_recursive_parent_name()
    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def create(self, vals):
        res = super().create(vals)
        user_write_vals = {'user_program_ids': [Command.link(res.id)]}
        if not self.env.user.user_program_id:
            user_write_vals['user_program_id'] = res.id
        self.env.user.write(user_write_vals)
        return res
    #
    # def write(self, vals):
    #     res = super().write(vals)
    #     return res
