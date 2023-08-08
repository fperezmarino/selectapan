# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command
import logging

logger = logging.getLogger(__name__)


class EnrollStudentFormStudent(models.TransientModel):
    _name = 'enroll.student.form.student'
    _description = 'Enroll student form student'
    _inherit = 'enroll.student.form.individual'

    enrollment_state_ids = fields.One2many('enroll.student.form.student.enrollment.state', 'student_id')
    family_ids = fields.Many2many(
        'enroll.student.form.family',
        relation='enroll_student_form_student_family_rel',
        column1='student_id',
        column2='family_id',
        )
    real_student_id = fields.Many2one('school.student', string="Real student")

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
            'family_ids': [Command.set(self.mapped('family_ids.real_family_id').ids)],
            'enrollment_state_ids': [Command.create(enroll_state.prepare_values()) for enroll_state in self.enrollment_state_ids],
            }
