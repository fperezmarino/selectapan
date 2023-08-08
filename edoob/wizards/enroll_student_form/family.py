# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command
import logging

logger = logging.getLogger(__name__)


class EnrollStudentFormFamily(models.TransientModel):
    _name = 'enroll.student.form.family'
    _description = "School enroll form family"

    @api.model
    def default_get(self, fields_list):
        context = self._context
        res = super().default_get(fields_list)

        form_id = context.get('default_form_id', False)

        form = self.env['enroll.student.form'].browse(form_id)
        if form and 'student_ids' in fields_list and not res.get('student_ids'):
            res['student_ids'] = [Command.set(form.student_ids.ids)]

        if context.get('real_family_id', False):
            FormFamilyEnv = self.env['school.family'].sudo()
            existing_family = FormFamilyEnv.browse(context['real_family_id'])
            existing_family_values = existing_family.prepare_enroll_form_family_default_values()
            res.update(existing_family_values)
        elif form:
            individuals_values = form.get_default_individuals_values()
            individuals = self.env['enroll.student.form.individual'].sudo().create(individuals_values)
            individuals._compute_name()
            res['individual_ids'] = [Command.set(individuals.ids)]
        return res

    form_id = fields.Many2one('enroll.student.form', required=True, ondelete='cascade', default=12)
    real_family_id = fields.Many2one('school.family')
    name = fields.Char(required=True, default='New family')

    form_student_ids = fields.Many2many('enroll.student.form.student', string="Form students", compute='compute_form_student_ids')
    student_ids = fields.Many2many(
        'enroll.student.form.student', domain="[('id', 'in', form_student_ids)]",
        relation='enroll_student_form_student_family_rel',
        column1='family_id',
        column2='student_id',
        )
    individual_ids = fields.Many2many(
        'enroll.student.form.individual',
        relation='enroll_student_form_student_individual_rel',
        column1='family_id',
        column2='individual_id',
        domain="[('id', 'not in', real_individual_ids)]",
        )
    individual_names = fields.Char(compute='_compute_individual_names')
    real_individual_ids = fields.Many2many('school.family.individual', store=False, compute='compute_real_individual_ids')
    individual_in_form_ids = fields.Many2many('enroll.student.form.individual', store=False, related='form_id.individual_ids')
    real_individual_in_form_ids = fields.Many2many('school.family.individual', store=False, compute='compute_real_individual_in_form_ids')

    @api.depends('individual_ids', 'individual_ids.real_individual_id')
    def compute_real_individual_ids(self):
        for form in self:
            form.real_individual_ids = form.mapped('individual_ids.real_individual_id')

    @api.depends('form_id', 'form_id.student_ids')
    def compute_form_student_ids(self):
        for family in self:
            family.form_student_ids = family.mapped('form_id.student_ids')

    @api.depends('form_id', 'individual_in_form_ids', 'form_id.individual_ids', 'form_id.individual_ids.real_individual_id')
    def compute_real_individual_in_form_ids(self):
        for family in self:
            family.real_individual_in_form_ids = family.mapped('individual_in_form_ids.real_individual_id')

    @api.onchange('form_id', 'individual_ids')
    def onchange_individual_ids(self):
        default_family_name = self._get_default_family_name()
        self.name = default_family_name

    def _get_default_family_name(self):
        self.ensure_one()
        individual1 = self.individual_ids[:1]
        individual1._compute_name()
        individual2 = self.individual_ids[1:2]
        individual2._compute_name()
        if individual1 and individual2:
            if individual1.last_name == individual2.last_name:
                return _("Family of %s, %s and %s", individual1.last_name, individual1.first_name, individual2.first_name)
            return _("Family of %s, %s and %s, %s", individual1.last_name, individual1.first_name, individual2.last_name, individual2.first_name)
        elif individual1:
            return _("Family of %s", individual1.name)
        return _("New Family")

    @api.depends('individual_ids.name', 'individual_ids.first_name', 'individual_ids.middle_name', 'individual_ids.last_name')
    def _compute_individual_names(self):
        for family in self:
            self.individual_names = ','.join([individual.name for individual in family.individual_ids])

    def prepare_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            }
