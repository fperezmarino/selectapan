# -*- coding: utf-8 -*-
import re

def migrate(cr, version):
    # Enrollment student form is removed from this version
    cr.execute("UPDATE school_enrollment_status SET type = 'admissions' WHERE type = 'admission'")
    cr.execute("UPDATE school_enrollment_status SET type = 'preenrolled' WHERE type = 'pre_enrolled'")
