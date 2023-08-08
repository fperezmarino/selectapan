# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SchoolBaseMixinWithCode(models.AbstractModel):
    """ It is used mainly in system parameters models to produce a name like
        name - code or just name """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.mixin.with.code'
    _description = "Mixin code"

    ######################
    # Fields declaration #
    ######################
    display_name = fields.Char(compute='_compute_display_name')
    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    active = fields.Boolean(default=True)

    #
    def _get_name_with_code(self):
        self.ensure_one()
        if self.user_has_groups('base.group_no_one') and self.code:
            name = f"{self.name} ({self.code})"
        else:
            name = self.name
        return name

    def _compute_display_name(self):
        for record in self:
            record.display_name = record._get_name_with_code()
