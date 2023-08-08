# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime


class SchoolEnrollmentHistory(models.Model):
    _name = 'school.enrollment.history'
    _description = "Enrollment history"
    _order = 'timestamp DESC'

    student_id = fields.Many2one('school.student', string="Student", ondelete='set null')
    student_name = fields.Char()

    program_id = fields.Many2one(
        'school.program', string="Current program", required=True, default=lambda self: self.env.program)
    school_id = fields.Many2one('school.school', string="Current school", related='program_id.school_id')
    grade_level_id = fields.Many2one(
        'school.grade.level', string="Grade level",
        domain="[('program_id', '=', program_id)]")
    enrollment_status_id = fields.Many2one('school.enrollment.status', string="Current status", required=True)
    enrollment_sub_status_id = fields.Many2one(
        'school.enrollment.sub.status',
        domain="[('program_id', '=', program_id), ('status_id', '=', enrollment_status_id)]",
        string="Current sub status"
        )

    next_school_id = fields.Many2one('school.school', string="Next school", related='next_program_id.school_id')
    next_program_id = fields.Many2one('school.program', string="Next program", default=lambda self: self.env.program)
    next_grade_level_id = fields.Many2one(
        'school.grade.level', string="Next grade level",
        domain="[('program_id', '=', program_id)]")
    next_enrollment_status_id = fields.Many2one('school.enrollment.status', string="Next status")
    next_enrollment_sub_status_id = fields.Many2one(
        'school.enrollment.sub.status',
        domain="[('program_id', '=', next_program_id), ('status_id', '=', next_enrollment_status_id)]",
        string="Next sub status")

    enrolled_date = fields.Date(string="Enrolled date")
    graduation_date = fields.Date(string="Graduation date")
    withdraw_date = fields.Date(string="Withdraw date")

    timestamp = fields.Datetime(string="Date", required=True, default=fields.Datetime.now())
    note = fields.Char(string="Note")

    @api.constrains('enrollment_sub_status_id')
    def check_enrollment_sub_status_id(self):
        for record in self:
            sub_status = record.enrollment_sub_status_id
            status = record.enrollment_status_id
            if sub_status and sub_status.status_id != status:
                raise ValidationError(_("Sub status %s belong to %s", sub_status.name, status.name))

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.student_name = res.student_id.name
        return res
