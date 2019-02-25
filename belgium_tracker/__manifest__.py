# coding: utf-8
{
    'name': 'Belgium Tracker',
    'version': '1.0',
    'depends': [
        'mail',
        'website',
    ],
    'installable': True,
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/depute_views.xml',
        'views/parti_views.xml',
        'views/programme_views.xml',
        'views/seance_views.xml',
        'views/vote_views.xml',
        'views/actions_menus.xml',
        'templates/deputes_templates.xml',
        'wizard/import_deputes_views.xml',
        'wizard/wizard_actions_menus.xml',
        'data/website_menu.xml',
    ],
    'application': True,
}
