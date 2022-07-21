# -*- coding: utf-8 -*-
from elar import db
from .timestamp_mixin import TimestampMixin
from flask import g
from elar.common.exceptions import ValidationError


class ClientAccountUser(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_client_account_users'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    client_account_id = db.Column(db.BigInteger, db.ForeignKey('sb_client_accounts.id'))
    user_id = db.Column(db.BigInteger, db.ForeignKey('sb_users.id'))
    role_id = db.Column(db.BigInteger, db.ForeignKey('sb_roles.id'))
    is_active = db.Column(db.Boolean)

    user = db.relationship('User', foreign_keys='ClientAccountUser.user_id')
    account = db.relationship('ClientAccount', foreign_keys='ClientAccountUser.client_account_id')
    role = db.relationship('Role', foreign_keys='ClientAccountUser.role_id')

    @classmethod
    def create(cls, **kwargs):
        account_user = cls()
        account_user.created_by_id = g.user.id
        account_user.account_id = kwargs['account_id']
        account_user.user_id = kwargs['user_id']
        account_user.role_id = kwargs['role_id']
        return account_user

    def import_data(self, data):
        try:
            props = ['client_account_id', 'user_id', 'role_id']  # , 'phone']
            for prop in props:
                setattr(self, prop, data.get(prop, getattr(self, prop)))
        except KeyError as e:
            raise ValidationError(f'Invalid customer: missing {e.args[0]}')
        return self
