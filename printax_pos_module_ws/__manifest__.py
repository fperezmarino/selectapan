# coding: utf-8
###########################################################################
{
    "name": "PrinTax para POS (WorkStation)",

    "summary": """
        Módulo para la emisión de facturas fiscales a través del programa PrinTax desde el POS.
    """,

    "description": """
        Este módulo utiliza el programa PrinTax para emitir facturas en impresores fiscales desde
        el módulo de punto de venta (POS). Estos impresores están adaptados a la legislación de
        varios paises específicos, en esta versión Venezuela y Panamá.


        Para Odoo versión 15, Julio 2022.

        Esta versión envia el comando al PrinTax desde la estación de trabajo, está homologada con
        los módulos fiscales desarrollados por:

        Desarrollos PNP, C.A. para impresores Epson.
        TheFactory HKA para impresores Bixolon.
    """,
   

  "author": "Odoasys",
    "website": "https://odoasys-sales.odoo.com",
    "license": "LGPL-3",
    "version": "15.1.0.0",
    "category": "Sales/Point Of Sale",
    "colaborator": "Hernán N.",
    "depends": [ "point_of_sale","mail" ],
    "demo": [ ],
    "data": [
        "views/pos_config.xml",
        "views/pos_order_list.xml",
        "views/pos_payment_method.xml",
        "views/precio_dolar.xml",
        "data/method_paid.xml",
        'data/mail_templates.xml',
    ],
    "test": [ ],
    "qweb": [ ],
    "installable": True,
    "application": False,
    "assets": {
        "web.assets_backend": [ 
            "printax_pos_module_ws/static/src/css/pos.css",
            "printax_pos_module_ws/static/src/js/order_print_fisc.js",
            "printax_pos_module_ws/static/src/js/pos_fact_fiscal.js",
            "printax_pos_module_ws/static/src/js/pos_select_user_reminder.js",
        ],
        
        "web.assets_qweb": [ 
            "printax_pos_module_ws/static/src/xml/pos_fact_fiscal_view.xml",
            "printax_pos_module_ws/static/src/xml/test_pst.xml",
        ],
     },
}
