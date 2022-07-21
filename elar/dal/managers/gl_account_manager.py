# -*- coding: utf-8 -*-
from elar.models import AccountingAccount
from elar import db


class GLAccountManager:
    @staticmethod
    def get_account_by_code(account_code):
        return AccountingAccount.query.filter(
            db.and_(
                AccountingAccount.account_code == str(account_code),
                AccountingAccount.active.is_(True),
            )
        ).one()
