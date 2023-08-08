# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("ALTER TABLE school_family ADD COLUMN aux_partner_id INT")
    cr.execute("UPDATE school_family SET aux_partner_id = partner_id")
