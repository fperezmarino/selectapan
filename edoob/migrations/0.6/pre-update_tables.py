# -*- coding: utf-8 -*-
import re

def migrate(cr, version):
    # Enrollment student form is removed from this version
    cr.execute("DELETE FROM ir_model WHERE model='enroll.student.form'")
