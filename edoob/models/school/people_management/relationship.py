"""
Created on Feb 1, 2020

@author: LuisMora
"""
from odoo import models, fields, api, _


class SchoolBaseRelationship(models.Model):
    _name = 'school.student.relationship'
    _description = "Student relationship"

    student_id = fields.Many2one("school.student", string="Student", required=True, ondelete="cascade")
    individual_id = fields.Many2one("school.family.individual", string="Individual", required=True, ondelete="cascade")
    relationship_type_id = fields.Many2one(
        'school.student.relationship.type', required=True, string="Relationship type",
        default=lambda self: self.env['school.student.relationship.type'].get_default_other_relationship()
        )

    custody = fields.Boolean(string="Custody")
    correspondence = fields.Boolean(string="Correspondence")
    grade_related = fields.Boolean(string="Grade Related")
    family_portal = fields.Boolean(string="Family Portal")
    is_emergency_contact = fields.Boolean("Emergency contact")


class RelationshipType(models.Model):
    """ SubStatus for students """
    _name = 'school.student.relationship.type'
    _description = "Relationship Type"
    _order = "sequence"

    @api.model
    def get_default_parent_relationship(self):
        return self.env.ref('edoob.relationship_parent', raise_if_not_found=False)

    @api.model
    def get_default_other_relationship(self):
        return self.env.ref('edoob.relationship_other', raise_if_not_found=False)

    name = fields.Char(string="Relationship type", required=True, translate=True)
    key = fields.Char(string="Key", translate=False)
    type = fields.Selection([
        ('daughter', _("Daughter")),
        ('son', _("Son")),
        ('child', _("Child")),

        ('sibling', _("Sibling")),
        ('brother', _("Brother")),
        ('sister', _("Sister")),

        ('parent', _("Parent")),
        ('father', _("Father")),
        ('mother', _("Mother")),

        ('grandparent', _("Grandparent")),
        ('grandmother', _("Grandmother")),
        ('grandfather', _("Grandfather")),

        ('stepparent', _("Stepparent")),
        ('stepmother', _("Stepmother")),
        ('stepfather', _("Stepfather")),
        ('stepsibling', _("Stepsibling")),
        ('stepsister', _("Stepsister")),
        ('stepbrother', _("Stepbrother")),

        ('uncle', _("Uncle")),
        ('cousin', _("Cousin")),
        ('other', _("Other")),
        ], string="Type")
    sequence = fields.Integer(default=1)
