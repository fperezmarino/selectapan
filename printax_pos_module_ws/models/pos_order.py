# -*- coding: utf-8 -*-
# Módulo que define el método print_invoice, que envía la factura al impresor fiscal a traves de PrinTax
#
# Esta versión maneja dos operaciones, la primera se encarga de armar el mensaje y la segunda guarda los datos
# se hace de esta manera porque no se puede enviar un mensaje desde el servidor al PrinTax cuando el equipo está
# en la nube
#
# Versión 1.0.0 - 2020.09.11 - Hernán Navarro
# Versión 1.0.1 - 2020.09.27

import logging

from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
import base64
import requests
import json
import logging
from functools import partial
from itertools import groupby
import psycopg2
import pytz
import re
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
from odoo.tools import html2plaintext
from collections import defaultdict


_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    # definición de los campos que reciben la información que retorna el PrinTax
    ptx_fiscal_invoice = fields.Char("Número de factura fiscal impresa", size = 10)
    ptx_serial_printer = fields.Char("Serial del impresor fiscal", size = 12)
    ptx_printing_date = fields.Datetime('Fecha y hora de impresión de la factura fiscal')
    ptx_base_imponible = fields.Float('Total de la base imponible')
    ptx_impuesto_printer = fields.Float('IVA calculado por el impresor')
    ptx_reporte_z = fields.Char("Número de reporte Z asociado a la factura", size = 6)
    anulada = fields.Char("status en impresora", size = 6)
    order_currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    is_invoice = fields.Selection([('facturado', 'Facturado'),('nofacturado', 'No facturado'),('anulado', 'Anulado')],default='nofacturado',  # Establecer el valor predeterminado como 'nofacturado'
        string='Estado de la factura',
        help='Estado de la factura')


    # ___________________________________________________________________________________________
    @api.model
    def rate_c(self):
        rate_currency = 3
        company = self.env['res.company'].browse(self.env.company.id)

        currency = self.env.ref("base.USD")
        rate_currency = currency._get_conversion_rate(self.env.company.currency_id, currency, self.env.company, fields.Date.today()
        )
        return rate_currency

    @api.model
    def search_paid_order_ids(self, config_id, domain, limit, offset):
        print(self)
        """Search for 'paid' orders that satisfy the given domain, limit and offset."""
        default_domain = ['&', ('config_id', '=', config_id), '!', '|', ('state', '=', 'draft'), ('state', '=', 'cancelled'),('ptx_fiscal_invoice','!=',"")]
        real_domain = AND([domain, default_domain])
        ids = self.search(AND([domain, default_domain]), limit=limit, offset=offset).ids
        totalCount = self.search_count(real_domain)
        return {'ids': ids, 'totalCount': totalCount}

    # ___________________________________________________________________________________________
   
    def printax_reprint_invoice(self,origen,nro_orden):
        dicc = {}
        id_order = self.env['pos.order'].search([('pos_reference', 'like', '%' + nro_orden)])

        if id_order.ptx_fiscal_invoice:
            mdlOrder = self.env['pos.order'].sudo().browse(id_order.id)
            print('por qa')
            return {
                'tip': "ROK",
                'msg': id_order.ptx_fiscal_invoice, 
                'ord': id_order.id
            }
        
        else:
            mdlOrder = self.env['pos.order'].sudo().browse(id_order.id)

        # _logger.info("Get mlPrinter")
            mdlPrinter = self.env['pos.config'].sudo().browse(mdlOrder.config_id.id)
            mdlPartner = self.env['res.partner'].sudo().browse(mdlOrder.partner_id.id)

            if mdlPrinter.printax_currency.id == False:
                return {
                    'tip': "ERR",
                    'err': "Moneda de facturación de PrinTax no seleccionada",
                }

            dTasa = 1.0
            if mdlOrder.currency_id.id != mdlPrinter.printax_currency.id:
                mdlMoney = self.env['res.currency'].sudo().browse(mdlPrinter.printax_currency.id)
                dTasa = mdlMoney.rate

            dicc['TIP']= 'FAC'
            dicc['CAJA']= mdlPrinter.name
            if mdlPartner.vat:
                dicc['NRF']= mdlPartner.vat 

            if mdlPartner.name:
                dicc['CNM'] = mdlPartner.name 
            dicc['TXT'] = nro_orden 

            strAddress = ""
            if mdlPartner.street != False:
                strAddress = mdlPartner.street
            if mdlPartner.street2 != False:
                if strAddress != "":
                    strAddress += ", "
                strAddress += ", " + mdlPartner.street2
            if mdlPartner.city != False:
                if strAddress != "":
                    strAddress += ", "
                strAddress += mdlPartner.city

            if strAddress != "":
                dicc['address']=strAddress

            if mdlPartner.phone != False:
                dicc['telefono']=mdlPartner.phone 
            list_pdr =[]
            for lines in mdlOrder.lines:
                dic_pdr= {}
                mdlTax = self.env['account.tax'].sudo().browse(lines.tax_ids.id)
                if mdlTax.amount == False:
                    taxRate = "0"
                else:
                    taxRate = mdlTax.amount

                dPrecio = lines.price_unit * dTasa
                dic_pdr['taxRate'] = taxRate
                dic_pdr['dPrecio'] = dPrecio
                dic_pdr['qty'] = lines.qty
                dic_pdr['display_name'] = lines.display_name
                list_pdr.append(dic_pdr)
            dicc['PRD'] = list_pdr
            dicc['SUT'] = 1


            iCount = 0
            list_idp =[]
            for payment in mdlOrder.payment_ids:
                if payment.payment_method_id.printax_code == 4:
                    dicc['IGTF'] = True

                list_idp.append(payment.payment_method_id.printax_code )

               

            dicc['IDP'] =  list_idp

            
            json_str = json.dumps(dicc)  # Convertir el diccionario a una cadena JSON
            encoded_str = base64.b64encode(json_str.encode('utf-8')) 

            return {
                'tip': "COK",
                'msg': encoded_str, 
                'ord': id_order.id
            }
        
        
    

    def printax_print_invoice(self, origen, nro_orden, cedula="",nom=""):
        dicc= {}
        # _logger.info("printax_print_invoice - Entrando a la función")

        if origen == 1:
            # _logger.info("Origen = 1")
            id_order = self.env['pos.order'].search([('pos_reference', 'like', '%' + nro_orden)])
        elif origen == 3:

            return self.anulacion(nro_orden,cedula,nom)
        else:
            # _logger.info("Origen != 1")
            id_order = self.env['pos.order'].search([('name', '=', nro_orden)])

        # _logger.info("id_order: ")
        # _logger.info(id_order);
        # _logger.info("Get mlOrder")
        mdlOrder = self.env['pos.order'].sudo().browse(id_order.id)

        # _logger.info("Get mlPrinter")
        mdlPrinter = self.env['pos.config'].sudo().browse(mdlOrder.config_id.id)

        # Si el campo ptx_fiscal_invoice no es nulo es que ya se imprimió esta factura
        if mdlOrder.ptx_fiscal_invoice != False:
            cmd = "TIP=RFA\n"
            cmd += "FNO=" + mdlOrder.ptx_fiscal_invoice;
            cmd = base64.b64encode(cmd.encode('utf-8'))

            # _logger.info("Factura ya fué impresa")

            return {
                'tip': "ERR",
                'err': "Factura ya fué impresa",
            }

        # _logger.info("Get mdlPartner")
        mdlPartner = self.env['res.partner'].sudo().browse(mdlOrder.partner_id.id)

        if mdlPrinter.printax_currency.id == False:
            return {
                'tip': "ERR",
                'err': "Moneda de facturación de PrinTax no seleccionada",
            }

        dTasa = 1.0
        if mdlOrder.currency_id.id != mdlPrinter.printax_currency.id:
            mdlMoney = self.env['res.currency'].sudo().browse(mdlPrinter.printax_currency.id)
            dTasa = mdlMoney.rate

        cmd = "TIP=FAC\n"
        dicc['TIP']= 'FAC'
        dicc['CAJA']= mdlPrinter.name
        if mdlPartner.vat:
           dicc['NRF']= mdlPartner.vat 
        
            

        if mdlPartner.name:
            dicc['CNM'] = mdlPartner.name 
            
        cmd += "TXT=Orden " + nro_orden + "\n"
        dicc['TXT'] = nro_orden 

        strAddress = ""
        if mdlPartner.street != False:
            strAddress = mdlPartner.street
        if mdlPartner.street2 != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += ", " + mdlPartner.street2
        if mdlPartner.city != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += mdlPartner.city

        if strAddress != "":
            cmd += "TXT=" + strAddress + "\n"
            dicc['address']=strAddress

        if mdlPartner.phone != False:
            cmd += "TXT=Telefono " + mdlPartner.phone + "\n"
            dicc['telefono']=mdlPartner.phone 

        # Cada línea debe tener el porcentaje de IVA, este porcentaje debe estar registrado en el impresor fiscal
        # se coloca 0 cuando es exento de impuesto
        list_pdr =[]
        for lines in mdlOrder.lines:
            dic_pdr= {}
            cmd += "PRD="
            


            mdlTax = self.env['account.tax'].sudo().browse(lines.tax_ids.id)
            if mdlTax.amount == False:
                taxRate = "0"
            else:
                taxRate = mdlTax.amount

            dPrecio = lines.price_unit * dTasa

            cmd += str(taxRate) + ","
            dic_pdr['taxRate'] = taxRate
            dic_pdr['dPrecio'] = dPrecio
            dic_pdr['qty'] = lines.qty
            dic_pdr['display_name'] = lines.display_name
            cmd += str(str(dPrecio)) + ","
            cmd += str(lines.qty) + ","
            cmd += lines.display_name + "\n"
            list_pdr.append(dic_pdr)
        dicc['PRD'] = list_pdr
        cmd += "SUT=1\n"
        dicc['SUT'] = 1


        iCount = 0
        list_idp =[]
        for payment in mdlOrder.payment_ids:
            cmd += "IDP="
            if payment.payment_method_id.printax_code == 4:
                dicc['IGTF'] = True

            list_idp.append(payment.payment_method_id.printax_code )

            if payment.payment_method_id.printax_code < 10:
                cmd += "0"
                # list_idp.append(0)
            cmd += str(payment.payment_method_id.printax_code)

            iCount += 1

            if iCount != len(mdlOrder.payment_ids):
                cmd += ','
                cmd += str(round(payment.amount, 2))
                # list_idp.append(round(payment.amount, 2))
                cmd += '\n'
            else:
                cmd += '\n'

        dicc['IDP'] =  list_idp

        # _logger.info(cmd)
        print(dicc)
        json_str = json.dumps(dicc)  # Convertir el diccionario a una cadena JSON
        encoded_str = base64.b64encode(json_str.encode('utf-8')) 
        cmd = base64.b64encode(cmd.encode('utf-8'))
        # print(encoded_str)

        return {
            'tip': "COK",
            'ip': mdlPrinter.printax_ip,
            'port': mdlPrinter.printax_port,
            'msg': encoded_str,  # .decode("utf-8")
            'ord': id_order.id
        }

    def update_invoice(self, nro_orden, strFac, strSer, strFec, strVta, strIva, strRpz):
        
        fecha_original = strFec
        fecha_objeto = datetime.strptime(fecha_original, '%H:%M:%S %d-%m-%Y')
        fecha_formateada = fecha_objeto.strftime('%Y-%m-%d %H:%M:%S')
        mdlOrder = self.env['pos.order'].sudo().browse(nro_orden)
        mdlOrder.update(
        {
            'ptx_fiscal_invoice': strFac,
            'ptx_serial_printer': strSer,
            'ptx_printing_date': fecha_formateada,
            'ptx_base_imponible': strVta,
            'ptx_impuesto_printer': strIva,
            'ptx_reporte_z': strRpz,
             'is_invoice':'facturado',
        })


    def update_invoice_anulada(self, nro_orden):
        id_order = self.env['pos.order'].search([('name', '=', nro_orden)])
        print(id_order)
        id_order.update(
        {
            'anulada': 'Anulada',
            'is_invoice':'anulada',
            
        })


    def anulacion(self,nro_orden, cedula="",nom=""):
        dicc={}
        id_order = self.env['pos.order'].search([('name', '=', nro_orden)])
        mdlOrder = self.env['pos.order'].sudo().browse(id_order.id)
        mdlPrinter = self.env['pos.config'].sudo().browse(mdlOrder.config_id.id)

        # Si el campo ptx_fiscal_invoice no es nulo es que ya se imprimió esta factura
        print(mdlOrder.ptx_fiscal_invoice )
        if mdlOrder.ptx_fiscal_invoice == False:
            return {
                'tip': "ERR",
                'err': "no hay factuara para anular ",
            }

        # _logger.info("Get mdlPartner")
        mdlPartner = self.env['res.partner'].sudo().browse(mdlOrder.partner_id.id)

        if mdlPrinter.printax_currency.id == False:
            return {
                'tip': "ERR",
                'err': "Moneda de facturación de PrinTax no seleccionada",
            }

        dTasa = 1.0
        if mdlOrder.currency_id.id != mdlPrinter.printax_currency.id:
            mdlMoney = self.env['res.currency'].sudo().browse(mdlPrinter.printax_currency.id)
            dTasa = mdlMoney.rate

        dicc['TIP']= 'ANU'
        dicc['CAJA']= mdlPrinter.name
        if mdlPartner.vat:
           dicc['NRF']= mdlPartner.vat 
        
            

        if mdlPartner.name:
            dicc['CNM'] = mdlPartner.name 

        dicc['TXT'] = nro_orden 

        strAddress = ""
        if mdlPartner.street != False:
            strAddress = mdlPartner.street
        if mdlPartner.street2 != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += ", " + mdlPartner.street2
        if mdlPartner.city != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += mdlPartner.city

        if strAddress != "":
            dicc['address']=strAddress

        if mdlPartner.phone != False:
            dicc['telefono']=mdlPartner.phone 

        # Cada línea debe tener el porcentaje de IVA, este porcentaje debe estar registrado en el impresor fiscal
        # se coloca 0 cuando es exento de impuesto
        list_pdr =[]
        for lines in mdlOrder.lines:
            dic_pdr= {}


            mdlTax = self.env['account.tax'].sudo().browse(lines.tax_ids.id)
            if mdlTax.amount == False:
                taxRate = "0"
            else:
                taxRate = mdlTax.amount

            dPrecio = lines.price_unit * dTasa

            dic_pdr['taxRate'] = taxRate
            dic_pdr['dPrecio'] = dPrecio
            dic_pdr['qty'] = lines.qty
            dic_pdr['display_name'] = lines.display_name
            list_pdr.append(dic_pdr)
        dicc['PRD'] = list_pdr
        dicc['SUT'] = 1


        iCount = 0
        list_idp =[]
        for payment in mdlOrder.payment_ids:
         
            if payment.payment_method_id.printax_code == 4:
                dicc['IGTF'] = True

            

        dicc['IDP'] =  list_idp

        # _logger.info(cmd)
        print(dicc)
        json_str = json.dumps(dicc)  # Convertir el diccionario a una cadena JSON
        encoded_str = base64.b64encode(json_str.encode('utf-8')) 
        
        # print(encoded_str)

        return {
            'tip': "COK",
            'ip': mdlPrinter.printax_ip,
            'port': mdlPrinter.printax_port,
            'msg': encoded_str,  # .decode("utf-8")
            'ord': id_order.id
        }



class Posseccion(models.Model):
    _inherit = 'pos.session'


    def get_closing_control_data(self):

        self.ensure_one()
        orders = self.order_ids.filtered(lambda o: o.ptx_fiscal_invoice)
        payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
        pay_later_payments = orders.payment_ids - payments
        cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
        default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
        total_default_cash_payment_amount = sum(payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped('amount')) if default_cash_payment_method_id else 0
        other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
        cash_in_count = 0
        cash_out_count = 0
        cash_in_out_list = []
        for cash_move in self.cash_register_id.line_ids.sorted('create_date'):
            if cash_move.amount > 0:
                cash_in_count += 1
                name = f'Cash in {cash_in_count}'
            else:
                cash_out_count += 1
                name = f'Cash out {cash_out_count}'
            cash_in_out_list.append({
                'name': cash_move.payment_ref if cash_move.payment_ref else name,
                'amount': cash_move.amount
            })

        return {
            'orders_details': {
                'quantity': len(orders),
                'amount': sum(orders.mapped('amount_total'))
            },
            'payments_amount': sum(payments.mapped('amount')),
            'pay_later_amount': sum(pay_later_payments.mapped('amount')),
            'opening_notes': self.opening_notes,
            'default_cash_details': {
                'name': default_cash_payment_method_id.name,
                'amount': self.cash_register_id.balance_start + total_default_cash_payment_amount +
                                             sum(self.cash_register_id.line_ids.mapped('amount')),
                'opening': self.cash_register_id.balance_start,
                'payment_amount': total_default_cash_payment_amount,
                'moves': cash_in_out_list,
                'id': default_cash_payment_method_id.id
            } if default_cash_payment_method_id else None,
            'other_payment_methods': [{
                'name': pm.name,
                'amount': sum(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('amount')),
                'number': len(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm)),
                'id': pm.id,
                'type': pm.type,
            } for pm in other_payment_method_ids],
            'is_manager': self.user_has_groups("point_of_sale.group_pos_manager"),
            'amount_authorized_diff': self.config_id.amount_authorized_diff if self.config_id.set_maximum_difference else None
        }

    def get_payment_summary(self):
        # Buscar los pagos asociados a la sesión actual
        payments = self.env['pos.payment'].search([('session_id', '=', self.id)])

        # Calcular los totales para cada método de pago
        payment_summary = defaultdict(float)
        for payment in payments:
            payment_summary[payment.payment_method_id.name] += payment.amount

        return payment_summary
    
    def update_closing_control_state_session(self, notes):

    
        payment_summary = self.get_payment_summary()
        print(payment_summary)
        total = 0
        html_list = "<ul>"
        for key, value in payment_summary.items():  # Corregido: agrega .items() aquí
            html_list += f"<li>{key}: {value}</li>"
            total += value
        html_list += "</ul>"
       


        template = self.env.ref('printax_pos_module_ws.email_template_account_move')
        subject = "Cierre ce caja  {}".format(str(self.config_id.name) + 'Fecha' + str(self.stop_at))
        body_html = f"""
            <h2>Detalle del Asiento Contable {self.name}</h2>
            <p>Número del asiento: {self.move_id.name}</p>
             { html_list}
            <p>Monto total: {total}</p>
        """

        template_vals = {
            'subject': subject,
            'body_html': body_html,
            'email_from': 'administrador@technology.aconingua.com',
            'email_to': 'administrador@technology.aconingua.com',  # Cambiar esto por el campo apropiado en tu modelo
            'res_id': self.id,
        }
        template.send_mail(self.id, email_values=template_vals, force_send=True)
     



        if self.state == 'closed':
            raise UserError(_('This session is already closed.'))
        # Prevent the session to be opened again.
        self.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
        self._post_cash_details_message('Closing', self.cash_register_difference, notes)


# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     @api.model_create_multi
#     def create(self, vals_list):
#         moves = super(AccountMove, self).create(vals_list)

#         for move in moves:
#             # Agregar el código para enviar el correo electrónico aquí
#             template = self.env.ref('nombre_modulo.nombre_plantilla_correo')  # Reemplaza 'nombre_modulo' y 'nombre_plantilla_correo' con el nombre correcto de tu módulo y plantilla de correo
#             template.send_mail(move.id, force_send=True)

#         return moves

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
       
        moves = super(AccountMove, self).create(vals_list)
        # for vals_dict in vals_list:
    
            # if 'journal_id' in vals_dict:
            #     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@############################################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            #     diario = self.env['account.journal'].search([('code', '=', 'POSS')], limit=1)
            #     if vals_dict['journal_id'] == diario.id:
            #         vals_dict['journal_id']
            #         print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            #         if diario:
            #             ultimo_asiento = moves.search([('journal_id', '=', diario.id)], order='date desc, id desc', limit=1)
            #             if ultimo_asiento:
                        
            #                 template = self.env.ref('printax_pos_module_ws.email_template_account_move')
            #                 subject = "Asunto personalizado para el movimiento de cuenta {}".format(ultimo_asiento.name)
            #             body_html = f"""
            #                 <h2>Detalle del Asiento Contable {ultimo_asiento.id}</h2>
            #                 <p>Número del asiento: {ultimo_asiento.id}</p>
            #                 <p>Descripción: { ultimo_asiento.date}</p>
            #                 <p>Monto total: {ultimo_asiento.amount_total}</p>
            #                 <h3>Cierre de Caja</h3>
            #                 <p>Total del cierre de caja: {ultimo_asiento.amount_total}</p>
            #                 <h3>Montos de los Asientos</h3>
            #             """

            #             template_vals = {
            #                 'subject': subject,
            #                 'body_html': body_html,
            #                 'email_from': 'administrador@technology.aconingua.com',
            #                 'email_to': 'administrador@technology.aconingua.com',  # Cambiar esto por el campo apropiado en tu modelo
            #                 'res_id': ultimo_asiento.id,
            #             }
            #             template.send_mail(ultimo_asiento.id, email_values=template_vals, force_send=True)

        return moves