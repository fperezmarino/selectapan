# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TourLocation(models.Model):
    _name = 'tour.location'
    _description = 'Details About Location For Tour Package'

    name = fields.Char(string='Name')
    cover_image = fields.Image(string='Cover Image')
    longitude = fields.Char(string='Longitude', size=13)
    latitude = fields.Char(string='Latitude', size=12)
    color = fields.Integer(string='Color')
    zip = fields.Char(string='Pin Code', size=6)
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")

    place_ids = fields.One2many('tour.place', 'location_id', string='Places')
    hotel_ids = fields.One2many('tour.hotel', 'location_id', string='Hotel')


class TourPlace(models.Model):
    _name = 'tour.place'
    _description = 'Details About Tour Place Per Location'

    name = fields.Char(string='Name')
    main_image = fields.Image(string='Main Image')
    longitude = fields.Char(string='Longitude', size=13)
    latitude = fields.Char(string='Latitude', size=12)
    visit_time = fields.Char(string='Visit Time')
    visit_type = fields.Selection([('free', 'Free'),
                                   ('paid', 'Paid')],
                                  string='Visit Type')
    location_id = fields.Many2one('tour.location', string='Location')
    image_ids = fields.One2many('location.images', 'place_id', string="Images")
    color = fields.Integer(string='Color')

    def name_get(self):
        data = []
        for rec in self:
            data.append((rec.id, '%s - %s' % (rec.name, rec.location_id.name)))
        return data

    def action_visit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Place',
            'res_model': 'tour.place',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current'
        }

    # Address
    zip = fields.Char(string='Pin Code', size=6)
    street = fields.Char(string='Street1')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one("res.country.state", string='State', readonly=False, store=True,
                               domain="[('country_id', '=?', country_id)]")


class TourHotel(models.Model):
    _name = 'tour.hotel'
    _description = 'Hotel Related Information Near Places'

    name = fields.Char(string='Nombre')
    image = fields.Image(string='Imagen')
    location_id = fields.Many2one('tour.location', string='Ubicación')
    phone = fields.Char(string='Contacto')
    website = fields.Char(string='Sitio web')
    place_id = fields.Many2one('tour.place', string='Lugar más cercano')
    image_ids = fields.One2many('location.images', 'hotel_id', string='Imágenes')
    room_ids = fields.One2many('hotel.room', 'hotel_id', string='Habitación')
    meal_ids = fields.One2many('hotel.meals', 'hotel_id', string='Comidas')
    facilities_ids = fields.Many2many('hotel.facilities', string='Instalaciones')
    check_in = fields.Float(string='Hora de entrada')
    check_out = fields.Float(string="Hora de salida")
    star = fields.Char(string="Estrella")

    def action_visit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel',
            'res_model': 'tour.hotel',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current'
        }

    # Address
    zip = fields.Char(string='Código postal', size=6)
    street = fields.Char(string='Calle 1')
    street2 = fields.Char(string='Calle 2')
    city = fields.Char(string='Ciudad')
    country_id = fields.Many2one('res.country', 'País')
    state_id = fields.Many2one("res.country.state", string='Estado', readonly=False, store=True,
                                domain="[('country_id', '=?', country_id)]")


class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room Details'
    _rec_name = 'room_type_id'

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    hotel_id = fields.Many2one('tour.hotel', string='Hotel')
    room_type_id = fields.Many2one('room.type', string='Tipo de habitación')
    price = fields.Monetary(string='Precio/día')
    cover_image = fields.Image(string='Imagen de portada')
    image_ids = fields.One2many('room.image', 'room_id', string='Imágenes')


class RoomType(models.Model):
    _name = 'room.type'
    _description = 'Details of Room type'
    _rec_name = 'room_type'

    room_type = fields.Char(string='Tipo de habitación')


class RoomImages(models.Model):
    _name = 'room.image'
    _description = 'Details About Room Images'
    _rec_name = 'room_id'

    image = fields.Image(string='Imágenes')
    room_id = fields.Many2one('hotel.room', string='Habitación')


class LocationImages(models.Model):
    _name = 'location.images'
    _description = 'Image Of Location Of Hotel and Places'

    title = fields.Char(string='Título')
    image = fields.Image(string='Imágenes')
    place_id = fields.Many2one('tour.place', string='Lugar')
    hotel_id = fields.Many2one('tour.hotel', string='Hotel')


class HotelMeals(models.Model):
    _name = 'hotel.meals'
    _description = 'Details About Hotel Meals'
    _rec_name = 'type'

    hotel_id = fields.Many2one('tour.hotel', string='Hotel')
    type = fields.Selection([('breakfast', 'Desayuno'),
                                ('lunch', 'Almuerzo'),
                                ('dinner', 'Cena'),
                                ('evening_snakes', 'Snacks de la tarde'),
                                ('combo', 'Combo'),
                                ('snakes', 'Snacks')],
                                string='Tipo de comida')
    food = fields.Char(string='Comida disponible')


class HotelFacilities(models.Model):
    _name = 'hotel.facilities'
    _description = 'Hotel Facilities and It Type'
    _rec_name = 'name'

    type = fields.Selection([('Free', 'Gratis'),
                            ('Paid', 'Pago')],
                            string='Tipo')
    name = fields.Char(string='Instalaciones')
    color = fields.Integer(string='Color')

    def name_get(self):
        data = []
        for rec in self:
            data.append((rec.id, '%s - %s' % (rec.name, rec.type)))
        return data
