# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class NameSorting(models.Model):
    """ This will be used for set up name sorting """
    _name = "school.name_sorting"
    _order = "sequence"
    _description = "This will be used for set up name sorting"

    name = fields.Char(string=_("Name"), required=True)
    suffix = fields.Char(string=_("Suffix"), trim=False)
    prefix = fields.Char(string=_("Prefix"), trim=False)
    sequence = fields.Integer(default=1)


class SchoolBaseSettings(models.TransientModel):
    """  Settings for school module """
    _inherit = "res.config.settings"

    def _get_name_sorting_setting_ids(self):
        """ Get the names settings and sort them """
        name_sorting_ids = \
            self.env.ref("edoob.name_sorting_first_name") + \
            self.env.ref("edoob.name_sorting_middle_name") + \
            self.env.ref("edoob.name_sorting_last_name")

        return name_sorting_ids.sorted()

    name_sorting_setting_ids = fields.Many2many(
        "school.name_sorting", string="Name Sorting",
        default=_get_name_sorting_setting_ids, store=True)
    name_sorting_example = fields.Char(
        string=_("Name Sorting Example"), trim=False, compute="_get_name_sorting_example")

    allow_edit_student_name = fields.Boolean(
        string=_("Allow edit student name"),
        config_parameter='school.allow_edit_student_name',
        default=False)
    allow_edit_parent_name = fields.Boolean(
        string=_("Allow edit parent name"),
        config_parameter='school.allow_edit_parent_name',
        default=False)
    allow_edit_person_name = fields.Boolean(
        string=_("Allow edit person name"),
        config_parameter='school.allow_edit_person_name',
        default=False)

    @api.onchange("name_sorting_setting_ids")
    def _onchange_name_sorting_setting_ids(self):
        name_order_relation = {
            self.env.ref("edoob.name_sorting_first_name").id: _("First"),
            self.env.ref("edoob.name_sorting_middle_name").id: _("Middle"),
            self.env.ref("edoob.name_sorting_last_name").id: _("Last")
            }

        name = ""
        sorted_name_sorting_ids = self.name_sorting_setting_ids.sorted("sequence")
        for sorted_name_id in sorted_name_sorting_ids:
            name += (sorted_name_id.prefix or "") + \
                    name_order_relation.get(sorted_name_id._origin.id, "") + \
                    (sorted_name_id.suffix or "")
        self.name_sorting_example = name

    def _get_name_sorting_example(self):
        self.name_sorting_example = self.env["school.family.individual"].format_name(_("First"), _("Middle"), _("Last"))

    def recompute_all_individuals_names(self):
        individuals = self.env['school.family.individual'].search([])
        individuals.auto_format_name()
