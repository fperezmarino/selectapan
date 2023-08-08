# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class TourCustomer(models.Model):
    _inherit = 'res.partner'


class TourEmployee(models.Model):
    _inherit = 'hr.employee'
