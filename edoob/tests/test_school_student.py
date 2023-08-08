# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo.fields import Command

import datetime
from dateutil.relativedelta import relativedelta


@tagged('-at_install', 'post_install')
class TestSchoolStudent(TransactionCase):

    @classmethod
    def getProgramValues(cls):
        return [{'school_id': cls.my_school.id, 'name': f"My program {i}"} for i in range(0, 10)]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = datetime.date.today()
        cls.admin_user = cls.env.ref('base.user_admin')

        # School structure objects
        cls.my_school = cls.env.ref('edoob.my_school')

        cls.programs = cls.env.ref('edoob.my_program')
        for program_values in cls.getProgramValues():
            cls.programs += cls.env['school.program'].create(program_values)

        cls.my_grade_level = cls.env.ref('edoob.my_grade_level')
        cls.enrolled_status = cls.env.ref('edoob.enrollment_status_enrolled')

        # Students
        cls.student1 = cls.env.ref('edoob.student_1')

        cls.student2 = cls.student1.copy()
        cls.student2.enrollment_history_ids.unlink()
        cls.student2.write({'enrollment_history_ids': [Command.create({
            'school_id': cls.programs[1].school_id.id,  # This is even more generic
            'program_id': cls.programs[1].id,
            'grade_level_id': cls.my_grade_level.id,
            'enrollment_status_id': cls.enrolled_status.id,
            'date_start': cls.today,
        })]})

    def test_compute_academics_fields_by_enrollment_history(self):
        self.student1.write({'enrollment_history_ids': [
            Command.create({
                'school_id': self.programs[1].school_id.id,
                'program_id': self.programs[1].id,
                'grade_level_id': self.my_grade_level.id,
                'enrollment_status_id': self.enrolled_status.id,
                'date_start': self.today - relativedelta(days=1),
                'date_end': self.today,
            }),
            Command.create({
                'school_id': self.programs[2].school_id.id,
                'program_id': self.programs[2].id,
                'grade_level_id': self.my_grade_level.id,
                'enrollment_status_id': self.enrolled_status.id,
                'date_start': self.today - relativedelta(months=2),
                'date_end': self.today - relativedelta(months=1),
            }),
            Command.create({
                'school_id': self.programs[3].school_id.id,
                'program_id': self.programs[3].id,
                'grade_level_id': self.my_grade_level.id,
                'enrollment_status_id': self.enrolled_status.id,
                'date_start': self.today + relativedelta(months=2),
                'date_end': self.today + relativedelta(months=1),
            })
        ]})

        # Check program_ids, school_ids, grade_level_ids are filled
        self.assertSetEqual(set(self.student1.program_ids), set(self.student1.mapped('enrollment_history_ids.program_id')))
        self.assertSetEqual(set(self.student1.school_ids), set(self.student1.mapped('enrollment_history_ids.school_id')))
        self.assertSetEqual(set(self.student1.grade_level_ids), set(self.student1.mapped('enrollment_history_ids.grade_level_id')))

        # Check current enrollment history only have program 0 and program 1
        # because the other ones are out of time range
        self.assertEqual(len(self.student1.current_enrollment_history_ids), 2)
        current_program0_history_line = self.student1.current_enrollment_history_ids.filtered(lambda l: l.program_id == self.programs[0])
        current_program1_history_line = self.student1.current_enrollment_history_ids.filtered(lambda l: l.program_id == self.programs[1])
        current_program2_history_line = self.student1.current_enrollment_history_ids.filtered(lambda l: l.program_id == self.programs[2])
        current_program3_history_line = self.student1.current_enrollment_history_ids.filtered(lambda l: l.program_id == self.programs[3])

        self.assertTrue(current_program0_history_line)
        self.assertTrue(current_program1_history_line)
        self.assertFalse(current_program2_history_line)
        self.assertFalse(current_program3_history_line)

    def test_filter_with_admin_user(self):
        students = self.env['school.student'].with_user(self.admin_user).search([])
        self.assertNotIn(self.student2, students, "Users shouldn't see an student from a different program")
        self.assertIn(self.student1, students, "Users should be able to see their programs' students")

    def test_filter_with_sudo_user(self):
        students = self.env['school.student'].sudo().search([])
        self.assertIn(self.student2, students, "Superuser should see every student without filters")
        self.assertIn(self.student1, students, "Superuser should see every student without filters")
