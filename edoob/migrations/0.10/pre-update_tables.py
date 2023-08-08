# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("DELETE FROM ir_model WHERE model IN ('school.family.individual.relationship', 'school.family.individual.relationship.type')")
    cr.execute("DELETE FROM ir_model_data WHERE model IN ('school.family.individual.relationship', 'school.family.individual.relationship.type')")
    cr.execute("ALTER TABLE IF EXISTS school_family_individual_relationship RENAME TO school_student_relationship")
    cr.execute("ALTER TABLE IF EXISTS school_family_individual_relationship_type RENAME TO school_student_relationship_type")
    cr.execute("ALTER SEQUENCE school_family_individual_relationship_id_seq RENAME TO school_student_relationship_id_seq")
    cr.execute("ALTER SEQUENCE school_family_individual_relationship_type_id_seq RENAME TO school_student_relationship_type_id_seq")

    # No more weird relationships
    cr.execute("ALTER TABLE school_student_relationship ADD COLUMN IF NOT EXISTS student_id INTEGER")
    cr.execute("UPDATE school_student_relationship ssr SET student_id = (SELECT id FROM school_student ss WHERE ss.individual_id = ssr.individual_id)")
    cr.execute("UPDATE school_student_relationship SET individual_id = individual_relation_id")
    cr.execute("DELETE FROM school_student_relationship WHERE student_id IS NULL")
