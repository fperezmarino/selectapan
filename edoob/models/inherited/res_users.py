# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
from odoo.fields import Command


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_school_id = fields.Many2one(
        'school.school', string="User school", compute_sudo='_compute_school_fields', store=True)
    user_school_ids = fields.Many2many(
        'school.school', 'res_school_users_rel', 'user_id', 'school_id', string="User schools",
        compute_sudo='_compute_school_fields', store=True)
    user_district_id = fields.Many2one('school.district', compute_sudo='_compute_school_fields', store=True)
    user_district_ids = fields.Many2many(
        'school.district', 'res_district_users_rel', 'user_id', 'district_id',
        compute_sudo='_compute_school_fields', store=True)

    user_program_id = fields.Many2one(
        'school.program', string='School program',
        help='The default program for this user.')
    user_program_ids = fields.Many2many(
        'school.program', 'res_program_users_rel', 'user_id', 'pid',
        string='School programs', default=lambda self: self.env.programs.ids)

    @api.constrains('user_program_id', 'user_program_ids')
    def _check_program(self):
        for user in self:
            if user.user_program_ids and not user.user_program_id:
                raise ValidationError(_('School program cannot be empty if you are assigning programs to an user (%s)', user.name))
            if user.user_program_ids and user.user_program_id not in user.user_program_ids:
                raise ValidationError(
                    _('School program %(proram_name)s is not in the allowed school programs for user %(user_name)s (%(program_allowed)s).',
                      proram_name=user.user_program_id.name,
                      user_name=user.name,
                      program_allowed=', '.join(user.mapped('user_program_ids.name')))
                )

    @api.onchange('user_program_ids')
    def onchange_program_ids(self):
        if self.user_program_id not in self.user_program_ids:
            self.user_program_id = self.user_program_ids[:1]._origin

    @api.depends('user_program_id', 'user_program_ids')
    def _compute_school_fields(self):
        for user in self:
            user.user_school_id = user.user_program_id.school_id
            user.user_school_ids = user.user_program_ids.mapped('school_id')
            user.user_district_id = user.user_program_id.school_id.district_id
            user.user_district_ids = user.user_program_ids.mapped('school_id.district_id')

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for values in vals_list:
            new_vals_list.append(self._remove_reified_groups(values))
        users = super().create(new_vals_list)
        group_multi_company_id = self.env['ir.model.data']._xmlid_to_res_id('school.group_multi_company', raise_if_not_found=False)
        if group_multi_company_id:
            for user in users:
                if len(user.company_ids) <= 1 and group_multi_company_id in user.groups_id.ids:
                    user.write({'groups_id': [Command.unlink(group_multi_company_id)]})
                elif len(user.company_ids) > 1 and group_multi_company_id not in user.groups_id.ids:
                    user.write({'groups_id': [Command.link(group_multi_company_id)]})
        return users

    def write(self, values):
        values = self._remove_reified_groups(values)
        res = super().write(values)
        if 'company_ids' not in values:
            return res
        group_multi_company = self.env.ref('base.group_multi_company', False)
        if group_multi_company:
            for user in self:
                if len(user.company_ids) <= 1 and user.id in group_multi_company.users.ids:
                    user.write({'groups_id': [Command.unlink(group_multi_company.id)]})
                elif len(user.company_ids) > 1 and user.id not in group_multi_company.users.ids:
                    user.write({'groups_id': [Command.link(group_multi_company.id)]})
        return res