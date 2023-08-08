# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo.fields import Command

import datetime
from dateutil.relativedelta import relativedelta


@tagged('-at_install', 'post_install')
class TestEnrollStudent(TransactionCase):

    @classmethod
    def getProgramValues(self):
        return {
            'program_setting_ids': [Command.create({'school_id': self.my_school.id,
                                                    'program_id': self.programs.id,
                                                    'grade_level_id': self.my_grade_level.id})]}
    @classmethod
    def getStudentData(self):
        return {'first_name': 'Test 1 First Name',
                 'last_name': 'Test 1 Last Name',
                 'date_of_birth': datetime.date.today(),
                 'gender': self.gender_female.id,
                 }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = datetime.date.today()
        cls.admin_user = cls.env.ref('base.user_admin')

        # School structure objects
        cls.my_school = cls.env.ref('edoob.my_school')
        cls.programs = cls.env.ref('edoob.my_program')
        cls.my_grade_level = cls.env.ref('edoob.my_grade_level')
        cls.enrolled_status = cls.env.ref('edoob.enrollment_status_enrolled')

        # Students
        cls.gender_female = cls.env.ref('edoob.gender_female')
        cls.student1.write(cls.getProgramValues())
        cls.student2 = cls.student1.copy()
        cls.student2.write(cls.getProgramValues())

    def test_enroll_student(self):
        self.assertTrue(self.enroll_ids)
        for line in self.enroll_ids:
            self.assertTrue(line.student_ids)
            self.assertTrue(line.new_family_ids)
            for fam in line.new_family_ids:
                self.assertEqual(self.student1, fam.student_id)

        for student in self.enroll_ids:
            student.enroll()



    # def test_filter_with_admin_user(self):
    #     students = self.env['school.student'].with_user(self.admin_user).search([])
    #     self.assertNotIn(self.student2, students, "Users shouldn't see an student from a different program")
    #     self.assertIn(self.student1, students, "Users should be able to see their programs' students")
    #
    # def test_filter_with_sudo_user(self):
    #     students = self.env['school.student'].sudo().search([])
    #     self.assertIn(self.student2, students, "Superuser should see every student without filters")
    #     self.assertIn(self.student1, students, "Superuser should see every student without filters")
