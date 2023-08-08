# -*- coding: utf-8 -*-
{
    'name': "Edoob - School management",

    'summary': """ School managements tools """,

    'description': """
        School managements tools 
    """,

    'author': "Eduweb Group",
    'website': "https://www.eduwebgroup.com",

    'version': '0.27',

    'depends': [
        'base',
        'portal',
        'contacts',
        'hr_skills',
        'calendar',
        ],

    'data': [

        # Wizards
        'wizards/edoob_migration_tool_view.xml',
        'wizards/enroll_student_form/enroll_student_form.xml',
        'wizards/enroll_student_form/student.xml',
        'wizards/enroll_student_form/family.xml',
        'wizards/enroll_student_form/individual.xml',

        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/relationships_rules.xml',
        'security/res_partner_rules.xml',
        'security/school_structure_rules.xml',

        # Records
        'data/school_records.xml',
        'data/enrollment_status.xml',

        'data/name_sorting.xml',
        'data/settings_default.xml',
        'data/gender_data.xml',
        'data/actions/res_partner_actions.xml',

        # Views
        'views/inherited/res_users_views.xml',
        'views/res_company.xml',

        'views/student_views.xml',
        'views/family_views.xml',
        'views/individual_views.xml',

        'views/settings/school_structure_views.xml',

        'views/portal_views.xml',
        'views/config_views.xml',

        'data/menudata.xml',
        ],

    'demo': [
        'demo/school_family_demo.xml',
        'demo/school_family_individual_demo.xml',
        'demo/school_student_demo.xml',
    ],
    'application': True,

    'assets': {
        'web.assets_qweb': [
            'edoob/static/src/xml/views.xml'
            ],
        'web.assets_backend': [
            'edoob/static/src/js/backend/*',
            'edoob/static/src/scss/*',

            # Libs
            'edoob/static/lib/jstree/dist/jstree.js',
            'edoob/static/lib/jstree/dist/themes/default/style.css',
            ],
        'web.assets_common': [
            'edoob/static/src/js/common/*',
            ],

        'web.tests_assets': [
            'edoob/static/tests/switch_school_menu.js'
            ]
    },

    'license': 'OPL-1',

    'post_init_hook': 'school_post_init_hook',
}
