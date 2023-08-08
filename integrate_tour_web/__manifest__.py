# -*- coding: utf-8 -*-
{
    'name': "integrate_tour_web",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','tk_tour_management','web'],
    'assets': {
        'web.assets_frontend': [
            'integrate_tour_web/static/src/css/offers_styles.css',
            'integrate_tour_web/static/src/css/offers_responsive.css',
            'integrate_tour_web/static/src/js/package.js',
            'integrate_tour_web/static/src/js/detail_pakage.js',
        ],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/package.xml',
        'views/templates.xml',
        'views/package_detalle.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
