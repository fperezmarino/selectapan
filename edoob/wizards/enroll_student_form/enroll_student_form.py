# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.fields import Command
import logging

logger = logging.getLogger(__name__)


def isInt(number):
    try:
        int(number)
        return True
    except ValueError:
        return False


class EnrollStudentForm(models.TransientModel):
    """ Enrollment Students Form """
    _name = 'enroll.student.form'
    _description = ' Enrollment Students Form '

    name = fields.Char("Name")

    # If you ask why aren't they just 1,2,3,4.
    # This is because this is supposed to be extended by any module and put its custom steps
    state = fields.Selection(
        selection=[
            ("0", "Students"),
            ("10", "Family"),
            ("20", "Relationship"),
            ('done', "Done"),
            ], default="0")

    student_ids = fields.One2many('enroll.student.form.student', 'form_id')
    individual_ids = fields.Many2many(
        'enroll.student.form.individual', store=False, compute='compute_individual_ids',
    )

    @api.depends('family_ids', 'family_ids.individual_ids')
    def compute_individual_ids(self):
        for form in self:
            form.individual_ids = form.mapped('family_ids.individual_ids')

    # Step 2
    family_ids = fields.One2many('enroll.student.form.family', 'form_id')
    real_family_ids = fields.Many2many('school.family', store=False, compute='compute_real_family_ids')

    # Step 3 - Relationships
    relationship_ids = fields.One2many('enroll.student.form.relationship', 'form_id', string="Relationships")

    def move_previous_step(self):
        self.ensure_one()
        prev_state = self.state
        form_states = self.get_sorted_form_states()
        if self.state != str(form_states[0]) and self.state != 'done':
            index = form_states.index(int(self.state))
            self.state = str(form_states[index - 1])
        elif self.state == 'done':
            self.state = str(form_states[-2])
        new_state = self.state
        self.on_move_step(prev_state, new_state)

    def move_next_step(self):
        self.ensure_one()
        prev_state = self.state
        if self.state != 'done' and isInt(self.state):
            form_states = self.get_sorted_form_states()
            index = form_states.index(int(self.state))
            self.state = str(form_states[index + 1])
        new_state = self.state
        self.on_move_step(prev_state, new_state)

    def on_move_step(self, prev_state, new_state):
        on_move_step_method_name = f'on_move_step_{new_state}'
        if hasattr(self, on_move_step_method_name):
            on_move_step_method = getattr(self, on_move_step_method_name)
            on_move_step_method(prev_state, new_state)

    def on_move_step_20(self, prev_state, new_state):
        self.recompute_relationships()

    def recompute_relationships(self):
        self.ensure_one()

        new_relationship_values = []
        student_individual_relations = []
        for family in self.family_ids:
            for student in family.student_ids:
                for individual in family.individual_ids:
                    if not any(filter(lambda vals: vals['student'] == student and vals['individual'] == individual, student_individual_relations)):
                        student_individual_relations.append({
                            'individual': individual,
                            'student': student,
                            })

        def should_be_added(_student, _individual):
            for _relationship in self.relationship_ids:
                if _relationship.student_id == _student and _relationship.individual_id == _individual:
                    return False
            return True

        def should_be_removed(_student, _individual):
            for _relation in student_individual_relations:
                if _relation['student'] == _student and _relation['individual'] == _individual:
                    return False
            return True

        for relation in student_individual_relations:
            student = relation['student']
            individual = relation['individual']
            if should_be_added(student, individual):
                new_relationship_values.append(Command.create({
                        'individual_id': individual.id,
                        'student_id': student.id,
                        'relationship_id': individual.default_relationship_id.id,
                    }))

        for relationship in self.relationship_ids:
            student = relationship.student_id
            individual = relationship.individual_id
            if should_be_removed(student, individual):
                new_relationship_values.append(Command.delete(relationship.id))

        self.update({'relationship_ids': new_relationship_values})

    def enroll(self):
        self._create_families()

        self._create_individuals()
        students = self._create_students()
        self._create_relationships()

        self._student_created()
        action = self.action_view_students(students)

        self.unlink()
        return action

    def _create_families(self):
        families = self.env['school.family']
        for form_family in self.family_ids:
            if not form_family.real_family_id:
                values = form_family.prepare_values()
                real_family = families.create(values)
                form_family.real_family_id = real_family
            families += form_family.real_family_id
        return families

    def _create_individuals(self):
        individuals = self.env['school.family.individual']
        for form_individual in self.mapped('family_ids.individual_ids'):
            values = form_individual.prepare_values()
            if not form_individual.real_individual_id:
                real_individual = individuals.create(values)
                form_individual.real_individual_id = real_individual
            else:
                form_individual.real_individual_id.write(values)
            individuals += form_individual.real_individual_id
        return individuals

    def _create_students(self):
        students = self.env['school.student']
        for form_student in self.student_ids:
            if not form_student.real_student_id:
                values = form_student.prepare_values()
                real_student = students.create(values)
                form_student.real_student_id = real_student
            students += form_student.real_student_id
        return students

    def _create_relationships(self):
        relationships = self.env['school.student.relationship']
        for form_relationship in self.relationship_ids:
            values = form_relationship.prepare_values()
            real_relationship = relationships.create(values)
            relationships += real_relationship
        return relationships

    def _student_created(self):
        """ Method to be inherited by any module if needed (e.g: edoob_finance) """
        pass

    @api.model
    def get_sorted_form_states(self):
        form_states_unfiltered = dict(self._fields['state']._description_selection(self.env)).keys()
        form_states = [int(state) for state in form_states_unfiltered if isInt(state)]
        form_states = sorted(form_states)
        form_states.append('done')
        return form_states

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super()._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            form_states = [str(state) for state in self.get_sorted_form_states()]
            form_states.remove('done')
            doc = etree.XML(result['arch'])
            statebar = doc.xpath("//form//field[@name='state']")
            first_step = form_states[0]
            last_step = form_states[-1]

            if statebar:
                statusbar_visible = ",".join(form_states)
                statebar[0].attrib['statusbar_visible'] = statusbar_visible

            step_groups = doc.xpath("//form//group[@edoob_step]")
            for group in step_groups:
                edoob_step = group.attrib['edoob_step']
                group.attrib['attrs'] = f"{{'invisible': [('state', '!=', '{edoob_step}')]}}"

            button_move_previous_step = doc.xpath("//form//button[@name='move_previous_step']")
            if button_move_previous_step:
                button_move_previous_step[0].attrib['attrs'] = f"{{'invisible': [('state', '=', '{first_step}')]}}"

            button_move_next_step = doc.xpath("//form//button[@name='move_next_step']")
            if button_move_next_step:
                button_move_next_step[0].attrib['attrs'] = f"{{'invisible': [('state', '=', '{last_step}')]}}"

            button_enroll = doc.xpath("//form//button[@name='enroll']")
            if button_enroll:
                button_enroll[0].attrib['attrs'] = f"{{'invisible': [('state', '!=', '{last_step}')]}}"
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    @api.depends('family_ids', 'family_ids.real_family_id')
    def compute_real_family_ids(self):
        for form in self:
            form.real_family_ids = form.mapped('family_ids.real_family_id')

    def new_virtual_family(self):
        family = self.env['enroll.student.form.family'].create({})
        family.onchange_individual_ids()
        return family.id

    def get_default_individuals_values(self):
        self.ensure_one()
        individuals_values = []
        default_last_name = self.get_default_last_name()
        for i in range(1, 3):
            values = {
                'first_name': _("Individual %s", i),
                'last_name': default_last_name,
                'form_id': self.id,
                }
            individuals_values.append(values)
        return individuals_values

    def get_default_last_name(self):
        return self.student_ids[:1].last_name

    @api.model
    def action_view_students(self, students):
        action = self.env["ir.actions.actions"]._for_xml_id("edoob.action_school_students")
        if len(students) > 1:
            action['domain'] = [('id', 'in', students.ids)]
        elif len(students) == 1:
            form_view = [(self.env.ref('edoob.school_student_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = students.id
        else:
            action = {
                'type': 'ir.actions.act_window_close'
                }
        action['target'] = 'main'
        return action
