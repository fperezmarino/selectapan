# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TourPackage(models.Model):
    _name = 'tour.package'
    _description = 'For Making tour Package and Manage Those package'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    package_seq = fields.Char(string='Sequence', required=True, readonly=True, default=lambda self: ('New'))
    name = fields.Char(string='Package')
    type = fields.Selection([('flexi_package', 'Flexi Package'),
                             ('group_package', 'Group  Package')],
                            string='Type', required=True, default='flexi_package')
    location_ids = fields.Many2many('tour.location', string="Locations")
    days_ids = fields.One2many('package.days', 'package_id', string='Days')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    price = fields.Monetary(string='Price/Person')
    tour_type = fields.Selection([('domestic', 'Domestic'), ('international', 'International')], string="Tour Type")
    season = fields.Selection([('winter', 'Winter'), ('summer', 'Summer'), ('monsoon', 'Monsoon')], string="Season")
    total_days = fields.Integer(string='Total Days')
    total_night = fields.Integer(string='Total Night')
    facilities_ids = fields.Many2many('package.facilities', string='Facilities')

    # Policies
    on_cancellation = fields.Html(string='Cancellation')
    on_date_change = fields.Html(string='Date Change')
    title_term_condition = fields.Html(string='Title')
    term_condition = fields.Html(string='Term & Condition')
    inclusion = fields.Html(string='Inclusion')
    exclusion = fields.Html(string='Exclusion')
    note = fields.Html(string='Note')
    payment = fields.Html(string='Payment')

    @api.model
    def create(self, vals):
        if vals.get('package_seq', ('New')) == ('New'):
            vals['package_seq'] = self.env['ir.sequence'].next_by_code(
                'tour.package') or ('New')
        res = super(TourPackage, self).create(vals)
        return res

    def name_get(self):
        data = []
        for rec in self:
            data.append((rec.id, '%s - %s' % (rec.package_seq, rec.name)))
        return data


class PackageDays(models.Model):
    _name = 'package.days'
    _description = 'Package Days'
    _rec_name = 'day'

    day = fields.Char(string="Days")
    package_id = fields.Many2one('tour.package', string='Package')
    activities_ids = fields.One2many('days.activities', 'day_id', string='Activities')
    hotel_id = fields.Many2one('tour.hotel', string="Hotels")
    location_ids = fields.Many2many(related='package_id.location_ids', string="Locations")
    places = fields.Char(string='Places Covered', compute='_compute_places')
    night_stay = fields.Char(string='Night')
    location_id = fields.Many2one('tour.location', string='Location')

    @api.depends('activities_ids')
    def _compute_places(self):
        for rec in self:
            place_string = ''
            if rec.activities_ids:
                for data in rec.activities_ids:
                    if data.place_id:
                        place_string = place_string + '[' + data.place_id.name + ']' + ' '
                        rec.places = place_string
                    else:
                        rec.places = place_string
            else:
                rec.places = ' '


class DaysActivities(models.Model):
    _name = 'days.activities'
    _description = 'Activiti related to Travel and Other Place'

    title = fields.Char(string='Title')
    distance = fields.Char(string='Distance')
    location_ids = fields.Many2many(related='day_id.location_ids', string="Locations")
    place_id = fields.Many2one('tour.place', string='Places')
    time = fields.Char(string='Time')
    from_destination = fields.Char(string='From')
    to_destination = fields.Char(string='To')
    start = fields.Float(string='Departure Time')
    end = fields.Float(string='Arrival Time')
    transfer = fields.Char(string='Transfer')
    day_id = fields.Many2one('package.days', string='Days')
    type = fields.Selection([('trip', 'Trip'),
                             ('sightseeing', 'Sight Seeing'),
                             ('hangout', 'Hangout')], string="Type")
    note = fields.Char(string="Note")
    duration = fields.Char(string='Duration')
    summary = fields.Text(string='Summary')


class PackageFacilities(models.Model):
    _name = 'package.facilities'
    _description = 'Package Facilities'

    name = fields.Char(string='Title')
    image = fields.Image(string='Image')
