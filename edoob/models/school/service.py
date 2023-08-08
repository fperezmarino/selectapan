# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import models, fields, exceptions


class Service(models.Model):
    _name = "school.service"
    _description = "School Service"

    name = fields.Char(string="Name")
