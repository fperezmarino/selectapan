# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class SchoolStudent(models.Model):
    """ Student model """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.student'
    _description = "Student"
    _inherits = {
        'school.family.individual': 'individual_id',
        }
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################

    # Demographics
    individual_id = fields.Many2one('school.family.individual', required=True, ondelete='restrict', string="Individual")
    student_status_id = fields.Many2one('school.enrollment.status')
    grade_level_id = fields.Many2one('school.grade.level')
    school_udid = fields.Char(string='School UDID')

    # Healthcare
    allergies_ids = fields.One2many("school.healthcare.allergy", "partner_id", string="Medical Allergies")
    conditions_ids = fields.One2many("school.healthcare.condition", "partner_id", string="Medical conditions")
    medications_ids = fields.One2many("school.healthcare.medication", "partner_id", string="Medical Medication")

    doctor_name = fields.Char("Doctor name")
    doctor_phone = fields.Char("Doctor phone")
    doctor_address = fields.Char("Doctor Direction")
    hospital = fields.Char("Hospital")
    hospital_address = fields.Char("Hospital Address")
    permission_to_treat = fields.Boolean("Permission To Treat")
    blood_type = fields.Char("Blood Type")

    # Academic
    enrollment_history_ids = fields.One2many('school.enrollment.history', 'student_id', copy=True)

    program_ids = fields.Many2many('school.program', store=True, compute='_compute_academics')
    school_ids = fields.Many2many('school.school', store=True, compute='_compute_academics')
    grade_level_ids = fields.Many2many(
        'school.grade.level', string="Grade Levels", store=True, compute='_compute_academics')
    district_ids = fields.Many2many('school.district', compute='_compute_academics', store=True)
    enrollment_status_ids = fields.Many2many(
        'school.enrollment.status', string="Enrollment status", store=True, compute='_compute_academics')

    # wizard related resource field
    wizard_student_id = fields.Integer()
    reference_id = fields.Char('Student Reference ID')

    # == Academics fields ==
    enrollment_state_ids = fields.One2many('school.student.enrollment.state', 'student_id', string="Enroll states")
    relationship_ids = fields.One2many('school.student.relationship', 'student_id', string="Relationships")
    homeroom = fields.Char(string="Homeroom")

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends(
        'enrollment_state_ids',
        'enrollment_state_ids.grade_level_id',
        'enrollment_state_ids.program_id',
        'enrollment_state_ids.enrollment_status_id',
        'enrollment_state_ids.enrollment_sub_status_id',
        )
    def _compute_academics(self):
        for student in self:
            enrollment_histories = student.enrollment_state_ids
            student.grade_level_ids = enrollment_histories.mapped('grade_level_id')
            student.program_ids = enrollment_histories.mapped('program_id')
            student.school_ids = student.program_ids.mapped('school_id')
            student.district_ids = student.school_ids.mapped('district_id')
            student.enrollment_status_ids = enrollment_histories.mapped('enrollment_status_id')

    def is_in_allowed_program(self):
        self.ensure_one()
        allowed_programs = self.env.programs.get_with_parent()
        return bool([p_id for p_id in self.program_ids if p_id in allowed_programs])

    ############################
    # Constrains and onchange  #
    ############################
    @api.onchange("first_name", "middle_name", "last_name")
    def onchange_student_name(self):
        self.name = self.individual_id.format_name(self.first_name, self.middle_name, self.last_name)

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not self.env.su and not self._context.get('no_program_filter', False):
            allowed_programs = self.env.programs.get_with_parent()
            program_domain = [('program_ids', 'in', allowed_programs.ids)]
            search_domain = expression.AND([program_domain, args])
        else:
            search_domain = args
        return super(SchoolStudent, self)._search(search_domain, offset, limit, order, count, access_rights_uid)

    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if not self.env.su and not self._context.get('no_program_filter', False):
            allowed_programs = self.env.programs.get_with_parent()
            program_domain = [('program_ids', 'in', allowed_programs.ids)]
            search_domain = expression.AND([program_domain, domain])
        else:
            search_domain = domain
        res = super()._read_group_raw(search_domain, fields, groupby, offset, limit, orderby, lazy)
        return res

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
    def open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'name': self.partner_name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            }

    def get_enroll_status_line(self, program_id: int):
        self.ensure_one()
        return self.enrollment_state_ids.filtered(lambda es: es.program_id.id == program_id)
