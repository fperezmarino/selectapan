# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class BookingWizard(models.TransientModel):
    _name = 'tour.booking.wizard'
    _description = 'Tour Booking Wizard for Book tour inside Customer and package'

    customer_id = fields.Many2one('res.partner', string='Customer')
    package_id = fields.Many2one('tour.package', string='Package')
    start_time = fields.Datetime(string='Tour Start Date')
    no_of_people = fields.Integer(string='No of People')

    def action_book_package(self):
        rec = self._context.get('active_id')
        data = {
            'package_id': self.package_id.id,
            'customer_id': self.customer_id.id,
            'start_datetime': self.start_time,
            'no_of_people': self.no_of_people
        }
        new_booking_id = self.env['tour.booking'].create(data)

        pipline_id = self.env['crm.lead'].browse(rec)

        pipline_id.write({'booking_id': new_booking_id.id})

        return True
