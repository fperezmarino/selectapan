# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class SchoolBaseIndividual(models.Model):
    """ School Family Individual """

    ######################
    # Private Attributes #
    ######################
    _name = 'school.family.individual'
    _description = "Family individual"
    _inherits = {
        'res.partner': 'partner_id',
        }
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    ###################
    # Default methods #
    ###################
    @api.model
    def _default_login(self):
        import time
        return 'individual%i' % int(time.time())

    ######################
    # Fields declaration #
    ######################
    partner_name = fields.Char(
        store=True, compute="_compute_name", inverse='_set_name', string="Contact name")

    user_id = fields.Many2one('res.users', string="User")
    partner_id = fields.Many2one('res.partner', required=True, readonly=False, ondelete='restrict', string="Related contact")

    active = fields.Boolean(default=True)

    first_name = fields.Char(required=True)
    middle_name = fields.Char()
    last_name = fields.Char(required=True)

    family_ids = fields.Many2many(
        'school.family',
        relation='individual_family_rel',
        column1='individual_id',
        column2='family_id', required=True, string="Families")
    family_student_ids = fields.Many2many(
        'school.student', string="Family Students",
        help="This are the students in the family",
        related='family_ids.student_ids')

    is_student = fields.Boolean(string="Is student", compute='compute_is_student', store=True)
    student_ids = fields.One2many('school.student', 'individual_id', string="Students (Technical)")
    family_student_ids = fields.Many2many('school.student', store=False, readonly=True, compute='compute_family_students')
    family_individual_ids = fields.Many2many(related='family_ids.individual_with_students_ids', string="Family individuals")

    relationship_ids = fields.One2many('school.student.relationship', 'individual_id', string="Relationships", readonly=False)

    # Demographics
    date_of_birth = fields.Date(string="Date of birth")
    gender = fields.Many2one('school.gender', string="Gender")
    email2 = fields.Char("Email 2")

    reference_id = fields.Char('Family Individual Reference ID')

    citizenship = fields.Char(string='Citizenship')
    ethnicity = fields.Char(string='Ethnicity')
    race = fields.Char(string='Race')

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        self.auto_format_name()

    @api.onchange("first_name", "middle_name", "last_name")
    def onchange_individual_name(self):
        self.auto_format_name()

    def _set_name(self):
        for individual in self:
            individual.partner_id.name = individual.partner_name

    @api.depends('student_ids')
    def compute_is_student(self):
        for individual in self:
            individual.is_student = bool(individual.student_ids)

    @api.depends('family_ids', 'family_ids.student_ids')
    def compute_family_students(self):
        for individual in self:
            individual.family_student_ids = individual.mapped('family_ids.student_ids') - individual.student_ids

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    def write(self, values):
        self._add_name_in_values_in_proper_format(values)
        res = super(SchoolBaseIndividual, self).write(values)
        self._fields_sync()
        return res

    @api.model
    def create(self, values):
        self._add_name_in_values_in_proper_format(values)
        res = super(SchoolBaseIndividual, self).create(values)
        self._fields_sync()
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not self.env.su and not self._context.get('no_program_filter', False):
            allowed_programs = self.env.programs.get_with_parent()
            program_domain = [
                '|', ('family_ids.student_ids', '=', False),
                '&', ('family_ids.student_ids', '!=', False),
                '|', ('family_ids.student_ids.program_ids', '=', False), ('family_ids.student_ids.program_ids', 'in', allowed_programs.ids)]
            search_domain = expression.AND([program_domain, args])
        else:
            search_domain = args
        return super()._search(search_domain, offset, limit, order, count, access_rights_uid)
    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
    def _fields_sync(self):
        pass

    def _add_name_in_values_in_proper_format(self, values):
        if 'name' not in values and ('first_name' in values or 'middle_name' in values or 'last_name' in values):

            def _get_from_values_or_record(key):
                if key in values:
                    return values[key]
                elif self:
                    return self[key]
                else:
                    return ''

            first_name = _get_from_values_or_record('first_name')
            middle_name = _get_from_values_or_record('middle_name')
            last_name = _get_from_values_or_record('last_name')
            values["name"] = self.format_name(first_name, middle_name, last_name)

    def auto_format_name(self):
        """ Use format_name method to create that """
        for individual in self:
            first = individual.first_name
            middle = individual.middle_name
            last = individual.last_name

            if any([first, middle, last]):
                individual.partner_name = individual.format_name(first, middle,
                                                                 last)
                individual.name = individual.format_name(first, middle, last)
            else:
                individual.partner_name = individual.partner_name
                individual.name = individual.name

    @api.model
    def format_name(self, first_name, middle_name, last_name):
        """
        This will format everything depending of school settings
        :return: A String with the formatted version
        """

        name_order_relation = {
            self.env.ref("edoob.name_sorting_first_name"):
                first_name or "",
            self.env.ref(
                "edoob.name_sorting_middle_name"): middle_name or "",
            self.env.ref("edoob.name_sorting_last_name"): last_name or ""
            }

        name_sorting_ids = self.env.ref(
            "edoob.name_sorting_first_name") + self.env.ref(
            "edoob.name_sorting_middle_name") + self.env.ref(
            "edoob.name_sorting_last_name")

        name = ""
        sorted_name_sorting_ids = name_sorting_ids.sorted("sequence")
        for sorted_name_id in sorted_name_sorting_ids:
            name = f"{name}{sorted_name_id.prefix or ''}{name_order_relation.get(sorted_name_id, '')}{(sorted_name_id.suffix or '')}"

        return name

    def open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'name': self.partner_name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            }

    def create_enroll_form_individuals(self):
        self.ensure_one()
        enroll_form_id = self._context.get('default_form_id', False)
        enroll_form = self.env['enroll.student.form'].browse(enroll_form_id)
        existing_individual_in_form = enroll_form.individual_ids.filtered(lambda ind: ind.real_individual_id == self)
        if existing_individual_in_form:
            return existing_individual_in_form.ids
        FormIndividualEnv = self.env['enroll.student.form.individual'].sudo()
        form_individual_ids = []
        for individual in self:
            values = individual._prepare_enroll_form_individual_values()
            form_individual = FormIndividualEnv.create(values)
            form_individual_ids.append(form_individual.id)
        return form_individual_ids

    def _prepare_enroll_form_individual_values(self):
        self.ensure_one()
        return {
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,

            'date_of_birth': self.date_of_birth,
            'gender': self.gender.id,
            'citizenship': self.citizenship,
            'ethnicity': self.ethnicity,
            'race': self.race,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'email2': self.email2,

            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'real_individual_id': self.id,
            'form_id': self._context.get('default_form_id', False),
            }
