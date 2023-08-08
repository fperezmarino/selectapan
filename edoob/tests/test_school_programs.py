# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged('-at_install', 'post_install')
class TestSchoolPrograms(TransactionCase):

    @classmethod
    def getProgramValues(cls):
        return [{'school_id': cls.my_school.id, 'name': f"My program {i}"} for i in range(0, 10)]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.super_user = cls.env.ref('base.user_root')
        cls.my_school = cls.env.ref('edoob.my_school')

        # School structure objects
        cls.my_school = cls.env.ref('edoob.my_school')

        cls.programs = cls.env.ref('edoob.my_program')
        for program_values in cls.getProgramValues():
            cls.programs += cls.env['school.program'].create(program_values)

    def test_created_school_program_is_in_user(self):
        """ This test that when an user creates a program, it is automatically appended to its allowed programs list """
        program = self.env['school.program'].with_user(self.admin_user).create({
            'school_id': self.my_school.id,
            'name': "Testing program",
            })
        self.assertIn(program, self.admin_user.user_program_ids)

    def test_user_context_values_for_programs(self):
        programs_ids = self.programs[:5].ids
        admin_programs_ids = self.programs[:3].ids
        self.admin_user.user_program_ids += self.programs[:3]
        context_admin_user = self.admin_user.with_context(allowed_program_ids=programs_ids)
        context_admin2_user = self.admin_user.with_context(allowed_program_ids=admin_programs_ids)
        context_super_user = self.super_user.with_context(allowed_program_ids=programs_ids)
        self.assertRaises(AccessError, lambda: context_admin_user.with_user(context_admin_user).env.programs)

        self.assertSetEqual(set(admin_programs_ids), set(context_admin2_user.with_user(context_admin2_user).env.programs.ids))
        self.assertSetEqual(set(programs_ids), set(context_super_user.with_user(context_super_user).env.programs.ids))
