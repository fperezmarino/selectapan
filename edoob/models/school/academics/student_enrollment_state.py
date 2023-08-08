# - *- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentEnrollState(models.Model):
    _name = 'school.student.enrollment.state'
    _description = "Student enrollment state"

    student_id = fields.Many2one('school.student', string="Student", required=True, ondelete='cascade')

    program_id = fields.Many2one('school.program', string="Current program", required=True)
    school_id = fields.Many2one('school.school', string="Current school", related='program_id.school_id')
    grade_level_id = fields.Many2one('school.grade.level', string="Grade level", domain="[('program_id', '=', program_id)]")
    enrollment_status_id = fields.Many2one('school.enrollment.status', string="Current status", required=True)
    enrollment_sub_status_id = fields.Many2one(
        'school.enrollment.sub.status',
        domain="[('program_id', '=', program_id), ('status_id', '=', enrollment_status_id)]",
        string="Current sub status"
        )

    next_program_id = fields.Many2one('school.program', string="Next program")
    next_school_id = fields.Many2one('school.school', string="Next school", related='next_program_id.school_id')
    next_grade_level_id = fields.Many2one(
        'school.grade.level', string="Next grade level",
        domain="[('program_id', '=', next_program_id)]")
    next_enrollment_status_id = fields.Many2one('school.enrollment.status', string="Next status")
    next_enrollment_sub_status_id = fields.Many2one(
        'school.enrollment.sub.status',
        domain="[('program_id', '=', next_program_id), ('status_id', '=', next_enrollment_status_id)]",
        string="Next sub status"
        )

    enrolled_date = fields.Date(string="Enrolled date")
    graduation_date = fields.Date(string="Graduation date")
    withdraw_date = fields.Date(string="Withdraw date")
    note = fields.Text(string="Note")

    _sql_constraints = [
        ('student_program_unique',
         'unique(student_id, program_id)',
         "You cannot have more than one enrollment state for the same student in the same program"),
        ]

    @api.model
    def create(self, vals):
        enrollment_state = super().create(vals)
        enrollment_state._log_action()
        return enrollment_state

    def write(self, vals):
        res = super().write(vals)
        if res:
            self._log_action()
        return res

    def _log_action(self):
        for enrollment_state in self:
            enrollment_history_values = enrollment_state._prepare_enrollment_history_values()
            self.env['school.enrollment.history'].create(enrollment_history_values)

    def _prepare_enrollment_history_values(self):
        self.ensure_one()
        return {
            'student_id': self.student_id.id,
            'program_id': self.program_id.id,
            'grade_level_id': self.grade_level_id.id,
            'enrollment_status_id': self.enrollment_status_id.id,
            'enrollment_sub_status_id': self.enrollment_sub_status_id.id,

            'next_program_id': self.next_program_id.id,
            'next_grade_level_id': self.next_grade_level_id.id,
            'next_enrollment_status_id': self.next_enrollment_status_id.id,
            'next_enrollment_sub_status_id': self.next_enrollment_sub_status_id.id,

            'enrolled_date': self.enrolled_date,
            'graduation_date': self.graduation_date,
            'withdraw_date': self.withdraw_date,

            'timestamp': fields.Datetime.now(),
            }

    @api.onchange('enrollment_status_id')
    def onchange_enrollment_status_id(self):
        self.enrollment_sub_status_id = False

    @api.onchange('program_id')
    def onchange_enrollment_program_id(self):
        self.grade_level_id = False
        self.enrollment_status_id = False
        self.enrollment_sub_status_id = False

    @api.onchange('enrollment_status_id')
    def onchange_enrollment_next_status_id(self):
        self.next_enrollment_sub_status_id = False

    @api.onchange('next_program_id')
    def onchange_enrollment_next_program_id(self):
        self.next_grade_level_id = False
        self.next_enrollment_status_id = False
        self.next_enrollment_sub_status_id = False

    ###############
    # Constraints #
    ###############
    @api.constrains('enrollment_sub_status_id')
    def check_enrollment_sub_status_id(self):
        for record in self:
            sub_status = record.enrollment_sub_status_id
            program = record.program_id
            status = record.enrollment_status_id
            if sub_status:
                if sub_status.status_id != status:
                    raise ValidationError(_("Sub status %s doesn't belong to %s", sub_status.name, status.name))
                elif sub_status.program_id != program:
                    raise ValidationError(_("Sub status %s doesn't belong to %s", sub_status.name, program.name))

    @api.constrains('enrollment_sub_status_id')
    def check_enrollment_sub_status_id(self):
        for record in self:
            sub_status = record.enrollment_sub_status_id
            status = record.enrollment_status_id
            if sub_status and sub_status.status_id != status:
                raise ValidationError(_("Sub status %s belong to %s", sub_status.name, status.name))

    @api.constrains('enrollment_sub_status_id')
    def check_enrollment_sub_status_id(self):
        for record in self:
            sub_status = record.enrollment_sub_status_id
            status = record.enrollment_status_id
            if sub_status and sub_status.status_id != status:
                raise ValidationError(_("Sub status %s belong to %s", sub_status.name, status.name))
