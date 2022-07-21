from elar import db
from .timestamp_mixin import TimestampMixin
from flask import url_for

from ..common.exceptions import ValidationError


class Contract(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_contracts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    accounting_client_account_id = db.Column(db.BigInteger, db.ForeignKey('sb_client_accounts.id'))
    client_account_id = db.Column(db.BigInteger, db.ForeignKey('sb_client_accounts.id'))
    accounting_account = db.relationship('ClientAccount', foreign_keys='Contract.accounting_client_account_id')
    client_account = db.relationship('ClientAccount', foreign_keys='Contract.client_account_id')

    def get_url(self):
        return url_for('api.get_contract', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'accounting_client_account_id': self.accounting_client_account_id,
            'client_account_id': self.client_account_id,
        }

    def import_data(self, data):
        try:
            self.accounting_client_account_id = data['accounting_client_account_id']
            self.client_account_id = data['client_account_id']
        except KeyError as e:
            raise ValidationError(f'Invalid contract data: {e.args[0]}')
