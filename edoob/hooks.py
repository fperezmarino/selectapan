
from odoo import api, SUPERUSER_ID
from odoo.fields import Command


def school_post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    program = env.ref('edoob.my_program')
    env['res.users'].search([]).write({
        'user_program_ids': [Command.link(program.id)],
        'user_program_id': program.id,
    })
    cr.execute("DELETE FROM ir_model WHERE model='generate.class.event.wizard'")
