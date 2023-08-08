# coding: utf-8
from odoo import api, models
from odoo.addons.website.models import ir_http


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def _eval_context(self):
        res = super(IrRule, self)._eval_context()
        res.update({
            'district_id': self.env.district.id,
            'district_ids': self.env.districts.ids,

            'school_id': self.env.school.id,
            'school_ids': self.env.schools.ids,

            'program_id': self.env.program.id,
            'program_ids': self.env.programs.ids,
            })
        return res

    def _compute_domain_keys(self):
        """ Return the list of context keys to use for caching
         ``_compute_domain``. """
        return super(IrRule, self)._compute_domain_keys() \
               + ['allowed_program_ids']
