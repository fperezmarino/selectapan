# -*- coding: utf-8 -*-
from odoo import models, fields, api

class tour_web(models.Model):
    _inherit = "tour.package"

    website_published = fields.Boolean(related=False, readonly=False)
    image = fields.Binary(string='Imagen')
    descuentos_web = fields.Integer(string='% Descuento')
    f_d_desde = fields.Date(string="Descuento desde")
    f_d_hasta = fields.Date(string="Descuento hasta")
    currency = fields.Many2one('res.currency', string='Moneda para mostar en la web')
    description = fields.Text(string="Descripcion para ser montada en la Web")
    reseña = fields.Text(string="reseña")
    # age_ids = fields.One2many('integrate_tour_web.age_discounts', 'id', string='descuentos por edad ')
    precio_rate = fields.Float(compute="_compute_precio_rate")
    divisa = fields.Float( compute="_divisa")
    # price = fields.Float()

    
    def _divisa(self):
        currency = self.env['res.currency'].sudo().search([('name', '=', 'USD')], limit=1)
        self.divisa  = round(self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency.id),
                                                                    ('name', '<=', fields.Date.today())], order='name DESC', limit=1).inverse_company_rate,2)

    @api.depends('price', 'divisa','company_id','currency')
    def _compute_precio_rate(self):
        for record in self:
            if record.currency:
                if record.currency == record.company_id.currency_id :
                    record.precio_rate = record.price
                    print('hola')
                else:
                    record.precio_rate = round( record.price / record.divisa,2)
                    print(record.currency.id , record.company_id.id)
            else:
                record.precio_rate = 0  
                    


    @api.onchange('currency')
    def cambiar_precio_(self):
        print(self.divisa, self.precio_rate)
        # for record in self:
        #     if record.currency.id == record.company_id.id :
        #         pass
        #     else:
        #         print(self.currency.name)


# class tour_web_age_discounts(models.Model):
#     _name = "integrate_tour_web.age_discounts"
#     _description = 'Details related To age discounts'

#     age_discounts = fields.Selection([('A', 'Adultos'), ('N', 'Niños')], string='Descuento')
#     age_since = fields.Integer(string='Edad desde')
#     age_until = fields.Integer(string='Edad Hasta')
#     discounts = fields.Float(string='Descuento',digits=(12,2))
#     type_discounts = fields.Selection([('fix', 'Precio fijo'), ('offer', 'Oferta(%)')], string='Descuento', default='fix')
#     description = fields.Text(string="Descripcion")
    

class resPartner_(models.Model):

    _inherit= 'res.partner'
    
    _sql_constraints = [('email', 'unique(email)', 'El Numero de Referencia debe ser unico'),]
  
