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
        'base', 'contacts', 'industry_fsm', 'hr', 'mail', 'activities', 'barcodes', 'documents', 'project', 'web_tree_dynamic_colored_field','web'],
    'data': [

        # Security
        'security/tags_security.xml',
        'security/ir.model.access.csv',



        # data
        'data/tags_sequence.xml',
        'data/mail_template.xml',



        # wizard
        'wizard/add_tags_wizard.xml',
        'wizard/add_comment_task.xml',

        # views
        'views/anomalie_views.xml',
        'views/tags_views.xml',
        'views/incident_extend.xml',
        'views/activitie_extend.xml',
        'views/res_company_extend.xml',



        # report
        'report/tags_template.xml',
        'report/report_views.xml',
    ],
    'assets': {
            'web.assets_qweb': ["tournee/static/src/xml/paperclip_attachment.xml"],
    },
    'installable': True,
}
