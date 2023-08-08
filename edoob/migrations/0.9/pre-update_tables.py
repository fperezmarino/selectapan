# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("DELETE FROM ir_model WHERE model='school.home.address'")
