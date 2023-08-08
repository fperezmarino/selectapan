# -*- coding: utf-8 -*-

from odoo import models, fields


class EnrollmentStatus(models.Model):
    """ Enrollment for students """
    _name = 'school.enrollment.status'
    _description = "Enrollment Status"
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(
        string="Key", 
        help="This is used mainly for web services")
    note = fields.Char(string="Description")
    type = fields.Selection([
        ('enrolled', 'Enrolled'),
        ('withdrawn', 'Withdrawn'),
        ('graduate', 'Graduate'),
        ('pre-enrolled', 'Pre-Enrolled'),
        ('inactive', 'Inactive'),
        ('admissions', 'Admissions'),
        ])
    sub_status_ids = fields.One2many('school.enrollment.sub.status', 'status_id')
    reference_id = fields.Char('Enrollment Status Reference ID')


class EnrollmentSubStatus(models.Model):
    """ Substatus for students """
    _name = 'school.enrollment.sub.status'
    _description = "Enrollment sub status"

    status_id = fields.Many2one('school.enrollment.status', string='Status')
    program_id = fields.Many2one('school.program', required=True, default=lambda self: self.env.program)
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")
    reference_id = fields.Char('Enrollment Sub Status Reference ID')
