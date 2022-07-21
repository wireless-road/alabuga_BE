from elar.notification import email_trigger as trigger
from elar.notification import EmailCategory

default_sections = [
    {
        'name': 'New User',
        'items': [
            {
                'status': {
                    'enabled': True
                },
                'sender': 'norely@snapbooks.app',
                'receivers': [],
                'sender_name': 'SnapBooks Corp.',
                'template': 'snapbooks/welcome.html',
                'template_is_file': True,
                'category': EmailCategory.NEW_USER,
                'trigger_name': trigger.NewUser.WELCOME,
                'description': 'Welcome to SnapBooks - Interactive Platform For Continuous Accounting',
                'receiver_name': 'New User',
                'subject': 'Welcome to the SnapBooks!',
                'tags': [
                    'first_name',
                    'last_name',
                ]
            },
            {
                'status': {
                    'enabled': True
                },
                'sender': 'norely@snapbooks.app',
                'receivers': [],
                'sender_name': 'Subscriber',
                'template': 'snapbooks/reset_password.html',
                'template_is_file': True,
                'category': EmailCategory.AUTHENTICATION,
                'trigger_name': trigger.Authentication.RESET_PASSWORD,
                'description': 'User want to reset password - a reset link will be sent to user email',
                'receiver_name': 'User',
                'subject': 'Reset Password',
                'tags': [
                    'reset_url',
                ]
            },
            {
                'status': {
                    'enabled': True
                },
                'sender': 'norely@snapbooks.app',
                'receivers': [],
                'sender_name': 'Client',
                'template': 'snapbooks/invite_account.html',
                'template_is_file': True,
                'category': EmailCategory.NEW_USER,
                'trigger_name': trigger.NewUser.INVITE_ACCOUNT,
                'description': 'Invite an accountant to join client account',
                'receiver_name': 'Accountant',
                'subject': 'Join {{ client_account }} on SnapBooks',
                'tags': [
                    'client_account',
                    'invited_url',
                ]
            },
        ]
    },
]


default_section_by_name = {section['name']: section
                           for section in default_sections}
