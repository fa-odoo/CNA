# -*- coding: utf-8 -*-
{
    'name': "Extend Odoo dynamic dashboard",
    'summary': """
        """,
    'description': """
        Transit time graph
    """,
    'author': "SYENTYS",
    'website': "http://www.syentys.com",
    'version': '0.1',
    
    'depends': ['odoo_dynamic_dashboard', 'activities'],

    'data': [
        'views/dashboard_block_views.xml',
    ],
    'installable': True,
}
