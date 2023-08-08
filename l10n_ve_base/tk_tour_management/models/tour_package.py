# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TourPackage(models.Model):
    _name = 'tour.package'
    _description = 'For Making tour Package and Manage Those package'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    package_seq = fields.Char(string='Secuencia', required=True, readonly=True, default=lambda self: ('Nuevo'))
    name = fields.Char(string='Paquete')
    type = fields.Selection([('flexi_package', 'Paquete Flexible'),
                             ('group_package', 'Paquete Grupal')],
                            string='Tipo', required=True, default='flexi_package')
    location_ids = fields.Many2many('tour.location', string="Ubicaciones")
    days_ids = fields.One2many('package.days', 'package_id', string='Días')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    price = fields.Monetary(string='Precio/Persona')
    tour_type = fields.Selection([('domestic', 'Doméstico'), ('international', 'Internacional')], string="Tipo de Tour")
    season = fields.Selection([('winter', 'Invierno'), ('summer', 'Verano'), ('monsoon', 'Monzón')], string="Temporada")
    total_days = fields.Integer(string='Días Totales')
    total_night = fields.Integer(string='Noches Totales')
    facilities_ids = fields.Many2many('package.facilities', string='Instalaciones')

    # Políticas
    on_cancellation = fields.Html(string='Cancelación')
    on_date_change = fields.Html(string='Cambio de Fecha')
    title_term_condition = fields.Html(string='Título')
    term_condition = fields.Html(string='Términos y Condiciones')
    inclusion = fields.Html(string='Inclusión')
    exclusion = fields.Html(string='Exclusión')
    note = fields.Html(string='Nota')
    payment = fields.Html(string='Pago')

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

    day = fields.Char(string="Días")
    package_id = fields.Many2one('tour.package', string='Paquete')
    activities_ids = fields.One2many('days.activities', 'day_id', string='Actividades')
    hotel_id = fields.Many2one('tour.hotel', string="Hoteles")
    location_ids = fields.Many2many(related='package_id.location_ids', string="Ubicaciones")
    places = fields.Char(string='Lugares Visitados', compute='_compute_places')
    night_stay = fields.Char(string='Noches de Estancia')
    location_id = fields.Many2one('tour.location', string='Ubicación')

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

    title = fields.Char(string='Título')
    distance = fields.Char(string='Distancia')
    location_ids = fields.Many2many(related='day_id.location_ids', string="Ubicaciones")
    place_id = fields.Many2one('tour.place', string='Lugares')
    time = fields.Char(string='Hora')
    from_destination = fields.Char(string='Desde')
    to_destination = fields.Char(string='Hasta')
    start = fields.Float(string='Hora de salida')
    end = fields.Float(string='Hora de llegada')
    transfer = fields.Char(string='Traslado')
    day_id = fields.Many2one('package.days', string='Días')
    type = fields.Selection([
        ('trip', 'Viaje'),
        ('sightseeing', 'Turismo'),
        ('hangout', 'Paseo')
    ], string="Tipo")
    note = fields.Char(string="Nota")
    duration = fields.Char(string='Duración')
    summary = fields.Text(string='Resumen')


class PackageFacilities(models.Model):
    _name = 'package.facilities'
    _description = 'Package Facilities'

    name = fields.Char(string='título')
    image = fields.Image(string='Image')
