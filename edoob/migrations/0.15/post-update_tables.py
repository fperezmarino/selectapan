# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE school_family sf SET name = (SELECT rp.name FROM res_partner rp WHERE rp.id = sf.aux_partner_id)")
    cr.execute("ALTER TABLE school_family DROP CONSTRAINT school_family_partner_id_fkey")
    cr.execute("DELETE FROM res_partner WHERE id IN (SELECT aux_partner_id FROM school_family)")
