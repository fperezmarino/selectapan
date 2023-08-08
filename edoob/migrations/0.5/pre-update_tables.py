# -*- coding: utf-8 -*-

def migrate(cr, version):
    model_table = 'school_student_relationship'
    old_field_name = 'financial_responsability'
    new_field_name = 'financial_responsibility'
    cr.execute(f'ALTER TABLE "{model_table}" RENAME COLUMN "{old_field_name}" TO "{new_field_name}"')
    cr.execute("DELETE FROM ir_model WHERE model='generate.class.event.wizard'")
    cr.execute("DELETE FROM ir_model WHERE model='enroll.student.form'")
