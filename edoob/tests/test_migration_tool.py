# -*- coding: utf-8 -*-
import json

from odoo.tests import TransactionCase, tagged
from odoo.fields import Command

import datetime
from dateutil.relativedelta import relativedelta

@tagged('-at_install', 'post_install')
class TestMigrationTool(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_admin = self.env.ref('base.partner_admin')
        self.partner_demo = self.env.ref('base.partner_demo')
        self.edoob_record_values = {
            'districts': [
                {
                    'name': "JSON District",
                    'company_ids': self.env.ref('base.main_company').ids,
                    'id': 'district_1'
                }
            ],
            'schools': [
                {
                    'name': "JSON School",
                    'id': 'school_1',
                    'district_id': 'district_1',
                }
            ],
            'programs': [
                {
                    'name': "JSON Program",
                    'id': 'program_1',
                    'school_id': 'school_1',
                }
            ],
            'period_categories': [
                {
                    'name': "JSON Period category",
                    'id': 'period_category_1',
                }
            ],
            'periods': [
                {
                    'name': "JSON Period",
                    'id': 'period_1',
                    'program_id': 'program_1',
                    'category_id': 'period_category_1',
                }
            ],
            'grade_levels': [
                {
                    'name': "JSON Grade levels",
                    'id': 'grade_level_1',
                    'program_id': 'program_1',
                }
            ],
            'families': [
                {
                    'id': 'family_1',
                    'name': "JSON Family 1",
                    'students': ['student_1', 'student_demo'],
                    'individuals': ['individual_1', 'individual_admin'],
                    'relationships': [
                        {'individual': 'individual_1', 'relation': 'student_1', 'relationship_type_id': self.env.ref('edoob.relationship_child').id},
                        {'individual': 'student_1', 'relation': 'individual_1', 'relationship_type_id': 'edoob.relationship_parent'},
                    ]
                }
            ],
            'students': [
                {
                    'id': 'student_1',
                    'first_name': "Student",
                    'middle_name': '1',
                    'last_name':  'JSON',
                    'enrollment_history': [
                        {
                            'school_id': 'school_1',
                            'program_id': 'program_1',
                            'grade_level_id': 'grade_level_1',
                            'enrollment_status_id': self.env.ref('edoob.enrollment_status_enrolled').id,
                        }
                    ],
                    'ssn': "SSN 1"
                },
                {
                    'id': 'student_demo',
                    'first_name': "Student",
                    'middle_name': '1',
                    'last_name':  'JSON',
                    'partner_id': self.partner_demo.id,
                    'enrollment_history': [
                        {
                            'school_id': 'school_1',
                            'program_id': 'program_1',
                            'grade_level_id': 'grade_level_1',
                            'enrollment_status_id': 'edoob.enrollment_status_admission',
                        }
                    ],
                    'ssn': "SSN 1"
                }
            ],
            'individuals': [
                {
                    'id': 'individual_1',
                    'first_name': "Individual",
                    'middle_name': '1',
                    'last_name':  'JSON',
                },
                {
                    'id': 'individual_admin',
                    'first_name': "Mitchel",
                    'last_name':  "Admin",
                    'partner_id': self.partner_admin.id
                },
            ]
        }

    def _get_migration_tool(self, json_values):
        migration_tool = self.env['edoob.migration.tool.wizard'].create({
            'select_method': 'custom',
            'generated_json': json.dumps(json_values)
        })
        return migration_tool

    def get_record_values_only_with_keys(self, *allowed_keys):
        for key in list(self.edoob_record_values.keys()):
            if key not in allowed_keys:
                self.edoob_record_values.pop(key)
        return self.edoob_record_values

    def create_district_school_and_programs(self, migration_tool, record_values):
        district = migration_tool.create_districts(record_values)
        school = migration_tool.create_schools(record_values)
        program = migration_tool.create_programs(record_values)
        return district, school, program

    def create_all_school_structure(self, migration_tool, record_values):
        district, school, program = self.create_district_school_and_programs(migration_tool, record_values)

        period_category = migration_tool.create_period_categories(record_values)
        period = migration_tool.create_periods(record_values)
        grade_level = migration_tool.create_grade_levels(record_values)

        return district, school, program, period_category, period, grade_level

    def test_create_district(self):
        record_values = self.get_record_values_only_with_keys('districts')
        migration_tool = self._get_migration_tool(record_values)
        district = migration_tool.create_districts(record_values)
        self.assertEqual(len(district), 1)
        self.assertEqual(record_values['districts'][0]['name'], district.name)

    def test_create_school(self):
        record_values = self.get_record_values_only_with_keys('districts', 'schools')
        migration_tool = self._get_migration_tool(record_values)
        migration_tool.create_districts(record_values)
        school = migration_tool.create_schools(record_values)
        self.assertEqual(len(school), 1)
        self.assertEqual(record_values['schools'][0]['name'], school.name)
        self.assertEqual(record_values['districts'][0]['real_record'], school.district_id)

    def test_create_program(self):
        record_values = self.get_record_values_only_with_keys('districts', 'schools', 'programs')
        migration_tool = self._get_migration_tool(record_values)
        district, school, program = self.create_district_school_and_programs(migration_tool, record_values)
        self.assertEqual(len(program), 1)
        self.assertEqual(record_values['programs'][0]['name'], program.name)
        self.assertEqual(record_values['schools'][0]['real_record'], program.school_id)

    def test_create_period_categories(self):
        record_values = self.get_record_values_only_with_keys('period_categories')
        migration_tool = self._get_migration_tool(record_values)
        period_category = migration_tool.create_period_categories(record_values)
        self.assertEqual(len(period_category), 1)
        self.assertEqual(record_values['period_categories'][0]['name'], period_category.name)

    def test_create_periods(self):
        record_values = self.get_record_values_only_with_keys('districts', 'schools', 'programs', 'period_categories', 'periods')
        migration_tool = self._get_migration_tool(record_values)
        district, school, program = self.create_district_school_and_programs(migration_tool, record_values)
        period_category = migration_tool.create_period_categories(record_values)
        period = migration_tool.create_periods(record_values)
        self.assertEqual(len(period_category), 1)
        self.assertEqual(record_values['period_categories'][0]['real_record'], period.category_id)
        self.assertTrue(record_values['programs'][0]['real_record'] == period.program_id == program)

    def test_create_grade_levels(self):
        record_values = self.get_record_values_only_with_keys('districts', 'schools', 'programs', 'grade_levels')
        migration_tool = self._get_migration_tool(record_values)
        district, school, program = self.create_district_school_and_programs(migration_tool, record_values)
        grade_level = migration_tool.create_grade_levels(record_values)
        self.assertEqual(len(grade_level), 1)
        self.assertTrue(record_values['programs'][0]['real_record'] == grade_level.program_id == program)

    def test_create_families(self):
        record_values = self.edoob_record_values
        migration_tool = self._get_migration_tool(record_values)
        migration_tool.create_school_structure_records(record_values)
        family = migration_tool.create_families(record_values)
        self.assertEqual(len(family), 1)
        self.assertEqual(record_values['families'][0]['name'], family.name)

    def test_create_students(self):
        record_values = self.edoob_record_values
        migration_tool = self._get_migration_tool(record_values)
        migration_tool.create_school_structure_records(record_values)
        students = migration_tool.create_students(record_values)
        self.assertEqual(len(students), 2)
        for i, student in enumerate(students):
            for name_field in ['first_name', 'middle_name', 'last_name']:
                self.assertEqual(record_values['students'][i].get(name_field, False), student[name_field])
        self.assertEqual(students[-1].partner_id, self.partner_demo)

    def test_create_individuals(self):
        record_values = self.edoob_record_values
        migration_tool = self._get_migration_tool(record_values)
        migration_tool.create_school_structure_records(record_values)
        individuals = migration_tool.create_individuals(record_values)
        self.assertEqual(len(individuals), 2)
        for i, individual in enumerate(individuals):
            for name_field in ['first_name', 'middle_name', 'last_name']:
                self.assertEqual(record_values['individuals'][i].get(name_field, False), individual[name_field])
        self.assertEqual(individuals[-1].partner_id, self.partner_admin)

    # todo: A unit test for updating the relationships must be made0
