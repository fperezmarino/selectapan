# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TourInquiry(models.Model):
    _inherit = 'crm.lead'

    package_id = fields.Many2one('tour.package', string='Package')
    booking_id = fields.Many2one('tour.booking', string='Booking No.')
