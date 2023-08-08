import requests
from bs4 import BeautifulSoup
from odoo import models, fields, api
from datetime import datetime, date
from datetime import date
import pytz




class DollarRate(models.Model):
    _name = 'dollar.rate'
    _description = 'Dollar Rate'

    value = fields.Float(string='Value', digits=(10, 2))


    @api.model
    def _cron_update_dollar_rate(self):
        tz = pytz.timezone('America/Caracas')
        now = datetime.now(tz)
        current_datetime = now.strftime('%H:%M:%S')
        if current_datetime > "04:59:00" and current_datetime < "05:01:00":
            url = 'https://www.bcv.org.ve/'
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            contenedor_dolar = soup.find('div', {'id': 'dolar'})
            valor_dolar = contenedor_dolar.find('strong').text.strip()
            rate = float(valor_dolar.replace(',', '.'))
            
            CurrencyRate = self.env['res.currency.rate']
            currency = self.env.ref("base.USD")
            today = date.today().strftime('%Y-%m-%d')
            
            companies = self.env['res.company'].search([])  # Reemplaza 'your.company.model' por el modelo de tu empresa
            
            for company in companies:
                company_model = self.env[company._name]
                existing_rate = CurrencyRate.search([('currency_id', '=', currency.id), ('name', '=', today), ('company_id', '=', company.id)])
                
                if existing_rate:
                    existing_rate.write({'inverse_company_rate': rate})
                else:
                    CurrencyRate.create({'currency_id': currency.id, 'name': today, 'inverse_company_rate': rate, 'company_id': company.id})

        
