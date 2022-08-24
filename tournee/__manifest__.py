# -*- coding: utf-8 -*-
{
    'name': "Tournées",
    'summary': """
        """,
    'description': """
        Activities
    """,
    'author': "SYENTYS",
    'website': "http://www.syentys.com",
    'version': '0.1',
    
    'depends': [
        'base', 'contacts', 'industry_fsm', 'hr', 'mail', 'activities', 'barcodes', 'documents', 'project', 'web_tree_dynamic_colored_field','web','documents_project', 'report_xlsx'],
    'data': [

        # Security
        'security/tags_security.xml',
        'security/ir.model.access.csv',



        # data
        'data/tags_sequence.xml',
        'data/mail_template.xml',



        # wizard
        'wizard/navire_time_report_wizard.xml',
        'wizard/navire_duration_wizard_view.xml',
        'wizard/add_tags_wizard.xml',
        'wizard/add_comment_task.xml',
        'report/navire_time_template.xml',

        # views
        'views/anomalie_views.xml',
        'views/tags_views.xml',
        'views/incident_extend.xml',
        'views/activitie_extend.xml',
        'views/tourne_views.xml',



        # report
        'report/report_views.xml',

        'report/tags_template.xml',
    ],
    'assets': {
            'web.assets_qweb': ["tournee/static/src/xml/paperclip_attachment.xml"],
    },
    'installable': True,
}
