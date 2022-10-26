# -*- coding: utf-8 -*-
{
    'name': "Activities",
    'summary': """
        """,
    'description': """
        Activities
    """,
    'author': "SYENTYS",
    'website': "http://www.syentys.com",
    'version': '0.1',
    
    'depends': [
        'base','contacts','industry_fsm','hr','mail',"web", 'report_xlsx'
    ],
    'data': [
        # security
        'security/activities_security.xml',
        'security/ir.model.access.csv',

        # data
        'data/sequence.xml',

        # views
        'views/incident.xml',
        'views/incident_type.xml',
        'views/lieu.xml',
        'views/activitie_type.xml',
        'wizard/incident_duration_wizard_view.xml',

        # report
        'report/layout.xml',
        'report/activity_template.xml',
        'report/report_views.xml',
        'report/anomalies_ronde.xml',

        # data
        'data/mail_template.xml',

    ],
    'installable': True,
}
