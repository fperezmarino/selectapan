# -*- coding: utf-8 -*-

"""
Author: Luis Malavé
Date: 2021-04-05
Yes, I know that Odoo tips say dont do this...
But... I am just grouping things together to get some kind of order without
modifying the __init__ over and over again...
"""

from odoo import models, fields, api, _
import datetime

from odoo.exceptions import UserError


class SchoolBasePartnerCurrentSchoolGrade(models.Model):
    """ It is used as M:N table """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.partner.current.school.grade'
    _description = "Partner current school grade"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    partner_id = fields.Many2one('res.partner', required=True)
    school_id = fields.Many2one('school.school', required=True)
    program_id = fields.Many2one('school.program', required=True)
    grade_level_id = fields.Many2one('school.grade.level', required=True)

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    _sql_constraints = [
        ('unique_partner_grade_level_relation',
         'unique(partner_id,school_id,program_id, grade_level_id)',
         'Error, a partner cannot have repeated grade level program relation'),
        ]
    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################


class SchoolBasePartnerNextSchoolGrade(models.Model):
    """ It is used as M:N table """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.partner.next.school.grade'
    _description = "Partner next school grade"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    partner_id = fields.Many2one('res.partner')
    school_id = fields.Many2one('school.school')
    grade_level_id = fields.Many2one('school.grade.level')

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################


class SchoolBaseGradeLevelType(models.Model):
    _name = 'school.grade.level.type'
    _description = "Grade level type"

    type = fields.Selection([
        ('elementary', _("Elementary")),
        ('middle_school', _("Middle school")),
        ('high_school', _("High school")),
        ], required=True)
    name = fields.Char(required=True)


class Placement(models.Model):
    """ An informative model for students """
    _name = 'school.placement'
    _description = "Placement"
    name = fields.Char(string="Placement", required=True, translate=True)
    key = fields.Char(string="Key")


class WithdrawReason(models.Model):
    """ Why does the student withdraw? """
    _name = 'school.withdraw_reason'
    _description = "Withdraw reasons"
    name = fields.Char(string="WithDraw Reason", required=True, translate=True)
    key = fields.Char(string="Key")

    def testg(self):
        pass


class MaritalStatus(models.Model):
    """ An informative model for students """
    _name = 'school.marital_status'
    _description = "Marital Status"
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")


class Gender(models.Model):
    _name = "school.gender"
    _description = "School gender"
    name = fields.Char("Gender", required=True, translate=True)
    key = fields.Char("Key")


