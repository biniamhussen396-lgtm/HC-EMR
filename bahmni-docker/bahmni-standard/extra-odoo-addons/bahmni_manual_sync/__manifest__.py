{
    'name': 'Bahmni Manual Sync Admin',
    'version': '16.0.1.0.0',
    'summary': 'Manual retry and monitoring for unsynced Bahmni orders and failed events',
    'category': 'Sales',
    'author': 'Bahmni Admin',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sync_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
