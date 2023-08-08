# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    printax_ip = fields.Char(string='IP del equipo que está ejecutando el PrinTax', default='192.168.1.100', size = 16)
    printax_port = fields.Char(string='Puerto IP del PrinTax', default='5125', size = 6)
    printax_currency = fields.Many2one('res.currency', string = "Moneda de factura fiscal")
    printax_ip_hidden = fields.Char(string='IP hidden',  size = 16)

    @api.constrains('pricelist_id', 'available_pricelist_ids', 'journal_id', 'invoice_journal_id', 'journal_ids')
    def _check_currencies(self):
        if self.pricelist_id not in self.available_pricelist_ids:
            raise ValidationError(_("The default pricelist must be included in the available pricelists."))
        if any(self.available_pricelist_ids.mapped(lambda pricelist: pricelist.currency_id != self.company_id.currency_id)):
            raise ValidationError(_("All available pricelists must be in the same currency as the company."))
        if self.invoice_journal_id.currency_id and self.invoice_journal_id.currency_id != self.company_id.currency_id:
            raise ValidationError(_("The invoice journal must be in the same currency as the company currency."))
        if self.journal_id.currency_id and self.journal_id.currency_id != self.company_id.currency_id:
            raise ValidationError(_("The sales journal must be in the same currency as the company currency."))
