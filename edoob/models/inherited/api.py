from odoo import _
from odoo.api import Environment
from odoo.exceptions import AccessError
from odoo.tools import lazy_property


def program(self):
    program_ids = self.context.get('allowed_program_ids', [])
    if program_ids:
        if not self.su:
            user_program_ids = self.user.user_program_ids.ids
            if user_program_ids:
                if any(did not in user_program_ids for did in program_ids):
                    raise AccessError(_("Access to unauthorized or invalid program."))
        return self['school.program'].browse(program_ids[0])
    return self.user.user_program_id


def programs(self):
    program_ids = self.context.get('allowed_program_ids', [])
    if program_ids:
        if not self.su:
            user_program_ids = self.user.user_program_ids.ids
            if user_program_ids:
                if any(did not in user_program_ids for did in program_ids):
                    raise AccessError(_("Access to unauthorized or invalid program."))
        return self['school.program'].browse(program_ids)
    return self.user.user_program_id


Environment.program = lazy_property(program)
Environment.programs = lazy_property(programs)


def school(self):
    return self.program.sudo().school_id


def schools(self):
    return self.programs.sudo().mapped('school_id')


Environment.school = lazy_property(school)
Environment.schools = lazy_property(schools)


def district(self):
    return self.school.sudo().district_id


def districts(self):
    return self.schools.sudo().mapped('district_id')


Environment.district = lazy_property(district)
Environment.districts = lazy_property(districts)
