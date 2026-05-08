{
    'name': 'Service Request Management',
    'version': '17.0.1.0.1',
    'summary': 'Module for managing internal service requests',
    'category': 'Services',
    'author': 'Zungg',
    'depends': ['base', 'mail','product','stock'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/sequence.xml',
        'data/laptop_sequence.xml',
        'data/email_templates.xml',

        'data/cron.xml',
        'views/laptop_view.xml',
        'views/service_request_views.xml',
        'wizard/service_request_reopen_wizard_view.xml',
        'report/report_action.xml',


        'report/service_request_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
