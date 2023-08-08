# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Contact(models.Model):
    """ Contact """
#
    ######################
    # Private Attributes #
    ######################
    _inherit = 'res.partner'

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    is_edoob_student = fields.Boolean("School student", compute='_compute_is_edoob_partner', store=True)
    is_edoob_partner = fields.Boolean("School partner", compute='_compute_is_edoob_partner', store=True)
    is_edoob_parent = fields.Boolean("School parent", compute='_compute_is_edoob_partner', store=True)
    is_edoob_individual = fields.Boolean("School individual", compute='_compute_is_edoob_partner', store=True)
    school_individual_ids = fields.One2many('school.family.individual', 'partner_id', string="Related individuals")
    student_ids = fields.One2many('school.student', 'partner_id', string="Related student")

    # Search fields

    # Address fields
    address_partner_link_id = fields.Many2one('res.partner', string="Address partner link")
    partner_with_address_link_as_me_ids = fields.One2many(
        'res.partner', 'address_partner_link_id', 
        string="Partner with address link as me")

    @api.constrains('address_partner_link_id')
    def _check_address_partner_link_id(self):
        for partner in self:
            if not partner._check_recursion('address_partner_link_id'):
                raise ValidationError(_("You cannot create recursive partner addresses"))

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends('school_individual_ids', 'student_ids')
    def _compute_is_edoob_partner(self):
        for partner in self:
            is_edoob_individual = bool(partner.school_individual_ids)
            is_edoob_student = bool(partner.student_ids)
            is_school_parent = is_edoob_individual and not is_edoob_student

            partner.is_edoob_partner = is_edoob_individual
            partner.is_edoob_individual = is_edoob_individual
            partner.is_edoob_parent = is_school_parent
            partner.is_edoob_student = is_edoob_student

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    def write(self, values):
        res = super().write(values)
        if 'address_partner_link_id' in values:
            for partner in self:
                if partner.address_partner_link_id:
                    partner.write(partner.address_partner_link_id._prepare_write_recursive_address_links_values())
        if 'address_partner_link_id' not in values:
            if set(values.keys()) & self._get_address_link_fields():
                self._update_recursive_address_links()
        return res

    @api.model
    def create(self, values):
        partner = super().create(values)
        #
        # if set(values.keys()) & self._get_address_link_fields():
        #     # if not self._context.get('skip_recursive_check', False):
        #     partner._update_recursive_address_links()
        return partner

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
    @api.model
    def _get_address_link_fields(self):
        return {'country_id', 'state_id', 'city', 'street', 'street2', 'zip'}

    def _update_recursive_address_links(self):
        for partner in self:
            partners_to_update = partner.address_partner_link_id + partner.partner_with_address_link_as_me_ids
            partners_to_update = partners_to_update.filtered(partner._check_partner_has_not_same_address_fields)
            partners_to_update.write(partner._prepare_write_recursive_address_links_values())
            # partners_to_update._update_recursive_address_links()

    def _check_partner_has_not_same_address_fields(self, partner):
        self.ensure_one()
        for field in self._get_address_link_fields():
            if self[field] != partner[field]:
                return True
        return False

    def _prepare_write_recursive_address_links_values(self):
        self.ensure_one()
        address_values = {}
        for field in self._get_address_link_fields():
            field_type = self.env['res.partner']._fields[field]
            if field_type.type == 'many2one':
                if self[field]:
                    address_values[field] = self[field].id
            else:
                address_values[field] = self[field]
        return address_values
