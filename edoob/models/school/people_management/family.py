# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command

# X2M methods codes
from odoo.osv import expression

ACTION_TYPE = 0
TYPE_CREATE = 0
TYPE_REPLACE = 6
TYPE_ADD_EXISTING = 4
TYPE_REMOVE_NO_DELETE = 3
TYPE_REMOVE_DELETE = 2


class SchoolFamily(models.Model):

    ######################
    # Private Attributes #
    ######################
    _name = 'school.family'
    _description = "Family"
    _inherit = [
        'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'avatar.mixin'
        ]

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    name = fields.Char()
    active = fields.Boolean(default=True)

    individual_with_students_ids = fields.Many2many(
        'school.family.individual', string="All Individuals including students",
        relation='individual_family_rel',
        column1='family_id',
        column2='individual_id')

    student_ids = fields.Many2many(
        'school.student', string="Students",
        store=True, compute='compute_student_ids', inverse='_set_student_ids')
    individual_ids = fields.Many2many(
        'school.family.individual', string="Individuals",
        relation='individual_family_rel',
        column1='family_id',
        column2='individual_id', domain=[('is_student', '=', False)])

    # wizard related resource field
    student_wizard_ids = fields.Char(default='')
    reference_id = fields.Char('Family Reference ID')

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends('individual_with_students_ids')
    def compute_student_ids(self):
        for family in self:
            family.student_ids = family.individual_with_students_ids.student_ids
            family.individual_ids = family.individual_with_students_ids.filtered(lambda i: not i.student_ids)

    def _set_student_ids(self):
        for family in self:
            family.individual_with_students_ids += family.student_ids.mapped('individual_id')

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not self.env.su and not self._context.get('no_program_filter', False):
            allowed_programs = self.env.programs.get_with_parent()
            program_domain = ['|', ('student_ids', '=', False), ('student_ids.program_ids', 'in', allowed_programs.ids)]
            search_domain = expression.AND([program_domain, args])
        else:
            search_domain = args
        return super(SchoolFamily, self)._search(search_domain, offset, limit, order, count, access_rights_uid)

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
    def open_family(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'school.family',
            'name': self.name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            }

    def prepare_enroll_form_family_default_values(self):
        self.ensure_one()
        individuals_values = [individual._prepare_enroll_form_individual_values() for individual in self.individual_ids]
        individuals = self.env['enroll.student.form.individual'].sudo().create(individuals_values)
        return {
            'name': self.name,
            'real_family_id': self.id,
            'individual_ids': [Command.set(individuals.ids)],
            'form_id': self._context.get('default_form_id', False),
            }
