from odoo import fields, models ,api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Campos existentes
    # name = fields.Char(string='Product Name', required=True)
    # list_price = fields.Float(string='Sale Price', digits=(16, 2))

    # Aquí agregarás el campo para el monto en dólares
    dollar_price = fields.Float(string='Precio para la venta en $', digits=(16, 2))
    bs_price = fields.Float(string='Precio para la venta en Bs', digits=(16, 2))
    list_price = fields.Float(string='Sale Price', compute='_compute_list_price', digits=(16, 2))
    preciocompleto = fields.Float(string='completo', compute='_compute_list_price', digits=(16, 2))
    is_generic_product = fields.Boolean(string="Es un Producto Genérico")

    # Agrega el campo para almacenar la última tasa de cambio del dólar
    dollar_exchange_rate = fields.Float(string='Dollar Exchange Rate', digits=(16, 6))

    # La función para calcular el precio de venta actualizado
    def calculate_updated_sale_price(self):
        for product in self:
            print("@@@@@@@@@@@@@@@@@@@@@@")
            if product.dollar_price and product.dollar_exchange_rate:
                updated_price = product.dollar_price * product.dollar_exchange_rate
                product.list_price = updated_price

    # Agrega un trigger para que se actualice automáticamente el precio de venta
    @api.onchange('taxes_id')
    def actualizar(self):
        currency = self.env.ref("base.USD")
        rate_currency = currency._get_conversion_rate(
            self.currency_id, currency, self.env.company, fields.Date.today()
        )
        
        for product in self:
            
            ptax=0

            if rate_currency and product.dollar_price:
                precio = (product.dollar_price / rate_currency)
                taxes = product.taxes_id.compute_all(precio, currency=currency, quantity=1)
                for tax in taxes['taxes']:
                    ptax=tax['amount']

                product.list_price = precio/ (1+(product.taxes_id.amount/100 ) )
            elif product.bs_price:
                
                taxes = product.taxes_id.compute_all(product.bs_price, currency=currency, quantity=1)
            
                product.list_price = product.bs_price / (1+(product.taxes_id.amount/100 ) )
            else:
                # Si la tasa de cambio no está definida, mantener el list_price original
                product.list_price = 0

    @api.depends('dollar_price', 'currency_id.rate','bs_price')
    def _compute_list_price(self):
        # Obtener la tasa de cambio del dólar
        currency = self.env.ref("base.USD")
        rate_currency = currency._get_conversion_rate(
            self.currency_id, currency, self.env.company, fields.Date.today()
        )
        
        for product in self:
            
            ptax=0

            if rate_currency and product.dollar_price:
                precio = (product.dollar_price / rate_currency)
                taxes = product.taxes_id.compute_all(precio, currency=currency, quantity=1)
                for tax in taxes['taxes']:
                    ptax=tax['amount']

                product.list_price = precio/ (1+(product.taxes_id.amount/100 ) )
            elif product.bs_price:
                
                taxes = product.taxes_id.compute_all(product.bs_price, currency=currency, quantity=1)
            
                product.list_price = product.bs_price / (1+(product.taxes_id.amount/100 ) )
            else:
                # Si la tasa de cambio no está definida, mantener el list_price original
                product.list_price = 0

   