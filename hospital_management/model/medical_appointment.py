# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class medical_appointment(models.Model):
	_name = "medical.appointment"
	_inherit = 'mail.thread'
	_description = "Medical Appointment"

	name = fields.Char(string="Appointment ID", readonly=True ,copy=True)
	is_invoiced = fields.Boolean(copy=False,default = False)
	institution_partner_id = fields.Many2one('res.partner',domain=[('is_institution','=',True)],string="Health Center")
	inpatient_registration_id = fields.Many2one('medical.inpatient.registration',string="Inpatient Registration")
	patient_status = fields.Selection([
			('ambulatory', 'Ambulatory'),
			('outpatient', 'Outpatient'),
			('inpatient', 'Inpatient'),
		], 'Patient status', sort=False,default='outpatient')
	patient_id = fields.Many2one('medical.patient','Patient',required=True)
	urgency_level = fields.Selection([
			('a', 'Normal'),
			('b', 'Urgent'),
			('c', 'Medical Emergency'),
		], 'Urgency Level', sort=False,default="b")
	appointment_date = fields.Datetime('Appointment Date',required=True,default = fields.Datetime.now())
	appointment_end = fields.Datetime('Appointment End',required=True)
	doctor_id = fields.Many2one('medical.physician','Physician',required=True)
	speciality_id = fields.Many2one('medical.speciality','Speciality',required=True)
	no_invoice = fields.Boolean(string='Invoice exempt',default=True)
	validity_status = fields.Selection([
			('invoice', 'Invoice'),
			('tobe', 'To be Invoiced'),
		], 'Status', sort=False,readonly=True,default='tobe')
	appointment_validity_date = fields.Datetime('Validity Date')
	consultations_id = fields.Many2one('product.product','Consultation Service',required=True)
	comments = fields.Text(string="Info")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirm'),('cancel','Cancel'),('done','Done')],string="State",default='draft')
	invoice_to_insurer = fields.Boolean('Invoice to Insurance')
	medical_patient_psc_ids = fields.Many2many('medical.patient.psc',string='Pediatrics Symptoms Checklist')
	medical_prescription_order_ids = fields.One2many('medical.prescription.order','appointment_id',string='Prescription')
	insurer_id = fields.Many2one('medical.insurance','Insurer')
	duration = fields.Integer('Duration')

	def _valid_field_parameter(self, field, name):
		return name == 'sort' or super()._valid_field_parameter(field, name)

	@api.onchange('patient_id')
	def onchange_name(self):
		ins_obj = self.env['medical.insurance']
		ins_record = ins_obj.search([('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
		if len(ins_record)>=1:
			self.insurer_id = ins_record[0].id
		else:
			self.insurer_id = False

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
		msg_body = 'Appointment created'
		for msg in self:
			msg.message_post(body=msg_body)
		result = super(medical_appointment, self).create(vals)
		return result


	@api.onchange('doctor_id')
	def onchange_doctor(self):
		if not self.doctor_id:
			self.speciality_id = ""
		doc = self.env['medical.speciality'].browse(self.doctor_id.id)
		self.speciality_id = doc.id

	@api.onchange('inpatient_registration_id')
	def onchange_patient(self):
		if not self.inpatient_registration_id:
			self.patient_id = ""
		inpatient_obj = self.env['medical.inpatient.registration'].browse(self.inpatient_registration_id.id)
		self.patient_id = inpatient_obj.patient_id.id

	def confirm(self):
		self.write({'state': 'confirmed'})

	def done(self):
		self.write({'state': 'done'})

	def cancel(self):
		self.write({'state': 'cancel'})

	def print_prescription(self):
		self.filtered(lambda s : s.state == 'draft').write({'state' : 'done'})
		if not self.medical_prescription_order_ids:
			raise UserError(_(' No Prescription Added  '))
		return self.env.ref('hospital_management.report_print_prescription').report_action(self)


	def view_patient_invoice(self):
		self.write({'state': 'cancel'})

	def create_invoice(self):
		lab_req_obj = self.env['medical.appointment']
		account_invoice_obj  = self.env['account.move']
		account_invoice_line_obj = self.env['account.move.line']

		lab_req = lab_req_obj
		if lab_req.is_invoiced == True:
			raise UserError(_(' Invoice is Already Exist'))
		if lab_req.no_invoice == False:
			res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
												'invoice_date': date.today(),
											 })

			invoice_line_vals = {
				'name': lab_req.consultations_id.name or '',
				'account_id': invoice_line_account_id,
				'price_unit':lab_req.consultations_id.lst_price,
				'product_uom_id':lab_req.consultations_id.uom_id.id,
				'quantity': 1,
				'product_id':lab_req.consultations_id.id,
			}
			res1 = res.write({'invoice_line_ids' :([(0,0,invoice_line_vals)]) })
			if res:
				lab_req.write({'is_invoiced': True})
				imd = self.env['ir.model.data']
				action = self.env.ref('account.action_move_out_invoice_type')
				list_view_id = imd.sudo()._xmlid_to_res_id('account.view_move_form')
				result = {
								'name': action.name,
								'help': action.help,
								'type': action.type,
								'views': [ [list_view_id,'form' ]],
								'target': action.target,
								'context': action.context,
								'res_model': action.res_model,
								'res_id':res.id,
							}
				if res:
					result['domain'] = "[('id','=',%s)]" % res.id
		else:
			 raise UserError(_(' The Appointment is invoice exempt'))
		return result

		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
