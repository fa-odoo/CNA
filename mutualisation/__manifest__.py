# -*- coding: utf-8 -*-
{
    'name': "mutualisation",

    'summary': """
                Ce module permet de : 
                    - optimiser le nombre de licences Utilisateurs
                    - Créer une identification par code pin
    """,

    'description': """
                Ce module permet de : 
                    - optimiser le nombre de licences Utilisateurs
                    - Créer une identification par code pin
    """,

    'author': "Syentys",
    'website': "http://www.syentys.fr",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale', 'tournee'],
    'data': [
        'views/athentification.xml',
        'views/res_users.xml',
        'views/employe.xml',
        'views/incident_extend.xml',
        'views/project_task_extend.xml',
        'views/anomalie_ronde_extend.xml',
        'views/res_company_views.xml',
    ],
}
