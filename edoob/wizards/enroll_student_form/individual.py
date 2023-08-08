# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command
import logging

logger = logging.getLogger(__name__)


class EnrollStudentFormIndividual(models.TransientModel):
    _name = 'enroll.student.form.individual'
    _description = "Enroll student form: individual"
    _inherit = 'image.mixin'
    _rec_name = 'name'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        form_id = self._context.get('default_form_id', False)
        if 'form_id' in fields_list and not res.get('form_id'):
            res['form_id'] = form_id

        if form_id:
            form = self.env['enroll.student.form'].browse(form_id)
            res['last_name'] = form.get_default_last_name()

        return res

    name = fields.Char(compute="_compute_name", store=False)

    first_name = fields.Char(required=True)
    middle_name = fields.Char()
    last_name = fields.Char(required=True)

    # Demographics
    date_of_birth = fields.Date(string="Date of birth")
    gender = fields.Many2one('school.gender', string="Gender")
    citizenship = fields.Char(string='Citizenship')
    ethnicity = fields.Char(string='Ethnicity')
    race = fields.Char(string='Race')

    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    email2 = fields.Char()
    form_id = fields.Many2one('enroll.student.form', required=True, ondelete='cascade')

    # Address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    family_ids = fields.Many2many(
        'enroll.student.form.family',
        relation='enroll_student_form_student_individual_rel',
        column1='individual_id',
        column2='family_id',
        )
    default_relationship_id = fields.Many2one(
        'school.student.relationship.type', ondelete='cascade',
        default=lambda self: self.env['school.student.relationship.type'].get_default_parent_relationship()
        )
    real_individual_id = fields.Many2one('school.family.individual', string="Real individual")

    @api.onchange('first_name', 'middle_name', 'last_name')
    @api.depends('first_name', 'middle_name', 'last_name')
    def _compute_name(self):
        for student in self:
            student.name = self.env['school.family.individual'].format_name(student.first_name, student.middle_name, student.last_name)

    def prepare_values(self):
        self.ensure_one()
        return {
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,

            'date_of_birth': self.date_of_birth,
            'gender': self.gender.id,
            'citizenship': self.citizenship,
            'ethnicity': self.ethnicity,
            'race': self.race,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'email2': self.email2,

            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'family_ids': [Command.link(family.id) for family in self.mapped('family_ids.real_family_id')],
            }


class EnrollStudentFormFamilyRelationships(models.TransientModel):
    _name = 'enroll.student.form.relationship'
    _description = "Enroll student form: relationship"
    _order = 'student_id, individual_id'

    form_id = fields.Many2one('enroll.student.form', required=True, ondelete='cascade')
    student_id = fields.Many2one('enroll.student.form.student', required=True, ondelete='cascade')
    individual_id = fields.Many2one('enroll.student.form.individual', required=True, ondelete='cascade')
    relationship_id = fields.Many2one('school.student.relationship.type', required=True, ondelete='cascade')

    def prepare_values(self):
        self.ensure_one()
        return {
            'student_id': self.student_id.real_student_id.id,
            'individual_id': self.individual_id.real_individual_id.id,
            'relationship_type_id': self.relationship_id.id,
            }