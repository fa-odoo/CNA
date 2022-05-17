# -*- coding: utf-8 -*-
{
    'name': "rapport_anomalie_rondes",

    'summary': """
        Rapport Anomalies rondes""",


    'author': "Syentys",
    'website': "http://www.syentys.com",
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'tournee', 'industry_fsm'],

    'data': [
        'security/ir.model.access.csv',
        'views/tags_task_anomalie.xml',
        'wizard/anomalie_report_wizard.xml',
        'report/paper.xml',
        'report/report_config.xml',
        'report/anomalie_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
