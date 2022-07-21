# -*- coding: utf-8 -*-
ROLE_SYS_ADMIN = 'SA'
ROLE_ACCOUNTING_ACCOUNT_OWNER = 'AA'
ROLE_CLIENT_ACCOUNT_OWNER = 'CA'
ROLE_BOOKKEEPER = 'BK'
ROLE_EMPLOYEE = 'EM'

ROLE_TEXTS = {
    ROLE_SYS_ADMIN: 'System/Admin',
    ROLE_ACCOUNTING_ACCOUNT_OWNER: 'Accounting Account Owner',
    ROLE_CLIENT_ACCOUNT_OWNER: 'Client Account Owner',
    ROLE_BOOKKEEPER: 'BookKeeper',
    ROLE_EMPLOYEE: 'Employee',
}

ROLE_CODES = {ROLE_TEXTS[code]: code for code in ROLE_TEXTS}
