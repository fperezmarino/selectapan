# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PeriodCategory(models.Model):
    """ Period category """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.period.category'
    _description = "School period category"
    _rec_name = 'display_name'

    name = fields.Char()
    display_name = fields.Char(compute='_compute_recursive_name', store=True)

    # key = fields.Char()
    # todo: David multiple keys

    parent_id = fields.Many2one('school.period.category')
    child_ids = fields.One2many('school.period.category', 'parent_id')
    reference_id = fields.Char()

    @api.depends('parent_id.name', 'name')
    def _compute_recursive_name(self):
        for period in self:
            period.display_name = period._get_recursive_parent_name()

    def _get_recursive_parent_name(self):
        self.ensure_one()
        name = self.name
        if self.parent_id:
            name = "%s / %s" % (self.parent_id._get_recursive_parent_name(), name)
        return name


class Period(models.Model):
    """ Period """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.period'
    _description = "School period"
    _order = 'date_start desc'
    _inherit = ['school.mixin.with.code', 'image.mixin']

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    name = fields.Char(translate=True)
    parent_name = fields.Char(compute='compute_parent_full_name', store=True)

    category_id = fields.Many2one('school.period.category', required=True)

    program_id = fields.Many2one(
        'school.program', store=True,
        required=True, readonly=False, compute='compute_program_id',
        recursive=True)
    # class_ids = fields.Many2many(
    #     'school.class', relation='class_period_rel',
    #     column1='period_id', column2='class_id')

    parent_id = fields.Many2one('school.period')
    child_ids = fields.One2many('school.period', 'parent_id')

    date_start = fields.Date(
        compute='compute_dates', store=True, readonly=False, recursive=True)
    date_end = fields.Date(
        compute='compute_dates', store=True, readonly=False, recursive=True)
    reference_id = fields.Char('Period Reference ID')

    @api.depends('parent_id', 'parent_id.display_name')
    def compute_parent_full_name(self):
        for period in self:
            if period.parent_id:
                period.parent_name = period.parent_id._get_recursive_parent_name()
            else:
                period.parent_name = period._get_recursive_parent_name()

    @api.depends('child_ids', 'child_ids.date_start', 'child_ids.date_end')
    def compute_dates(self):
        for period in self:
            if period.child_ids:
                first_child = period.child_ids.filtered(lambda x: x.date_start).sorted('date_start')
                last_child = period.child_ids.filtered(lambda x: x.date_start).sorted('date_start', reverse=True)

                period.date_start = first_child[0].date_start if first_child else False
                period.date_end = last_child[0].date_end if last_child else False
            else:
                period.date_start = False
                period.date_end = False

    # @api.constrains('date_start', 'date_end')
    # def _check_date_collision_constraint(self):
    #    """ Check that date doesn't collide with other sibling period """
    #    for period in self:
    #        sibling_periods = period.parent_id.child_ids - period
    #        for s_period in sibling_periods:
    #            period._check_collision(s_period)

    def _check_collision(self, other_period):
        """ We are going to use AABB collision inspiration"""
        self.ensure_one()
        other_period.ensure_one()
        if self.date_end >= other_period.date_start and self.date_start <= other_period.date_end:
            raise UserError(_("Date collision between %s and %s\n"
                              "Date range of %s (%s)-(%s)\n"
                              "Date range of %s (%s)-(%s)") % (
                                self.name, other_period.name,
                                self.name, self.date_start, self.date_end,
                                other_period.name, other_period.date_start,
                                other_period.date_end))

    def _get_period_recursive_parent_name(self):
        self.ensure_one()
        name = "%s / %s / %s / %s" % (self.program_id.school_id.district_id.name,
                                      self.program_id.school_id.name, self.program_id.name, self.name)
        if self.parent_id:
            name = " %s / %s" % (self.parent_id._get_period_recursive_parent_name(), name)

        return name

    def _compute_display_name(self):
        for period in self:
            period.display_name = period._get_period_recursive_parent_name()

    def _get_recursive_parent_name(self):
        self.ensure_one()
        name = self.name
        if self.parent_id:
            name = "%s / %s" % (self.parent_id._get_recursive_parent_name(), name)
        return name

    @api.model
    def display_name_depends(self):
        return ['code',
                'name',
                'parent_id',
                'parent_id.name',
                'parent_id.code',
                'parent_id.display_name']

    @api.depends(lambda self: self.display_name_depends())
    def compute_name(self):
        for record in self:
            record.display_name = record._get_recursive_parent_name()

    ##################
    # Compute method #
    ##################

    @api.depends('parent_id', 'parent_id.program_id')
    def compute_program_id(self):
        for period in self:
            if period.parent_id:
                period.program_id = period.parent_id.program_id
            else:
                period.program_id = False
