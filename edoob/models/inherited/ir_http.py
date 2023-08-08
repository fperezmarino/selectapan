# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(IrHttp, self).session_info()
        user = self.env.user

        if user.has_group('base.group_user'):
            programs = self.env.user.user_program_ids
            schools = programs.mapped('school_id')
            districts = schools.mapped('district_id')

            district_vals_list = districts.read(['name'])
            current_district_vals = district_vals_list[0] if district_vals_list else {}

            school_vals_list = []
            for i, school_vals, in enumerate(schools.read(['name'])):
                school_vals['district_id'] = schools[i].district_id.id
                school_vals_list.append(school_vals)

            current_school_vals = school_vals_list[0] if school_vals_list else {}

            program_vals_list = []
            for i, program_vals, in enumerate(programs.read(['name'])):
                program_vals['school_id'] = programs[i].school_id.id
                program_vals['parent_id'] = programs[i].parent_id.id
                program_vals['child_ids'] = programs[i].child_ids.ids
                program_vals_list.append(program_vals)
            current_program_vals = program_vals_list[0] if program_vals_list else {}

            session_info.update({
                'user_districts': {
                    'current_district': current_district_vals,
                    'allowed_districts': district_vals_list,
                },
                'user_schools': {
                    'current_school': current_school_vals,
                    'allowed_schools': school_vals_list,
                },
                'user_programs': {
                    'current_program': current_program_vals,
                    'allowed_programs': program_vals_list,
                },
                'display_switch_school_menu': bool(self.env.user.user_program_ids)
            })

        return session_info
