from elar.utils.string_utils import escape_str
from elar import db
from .timestamp_mixin import TimestampMixin
from flask import url_for

from ..common.exceptions import ValidationError


class AccountingAccount(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_accounting_accounts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    account_code = db.Column(db.String(12), nullable=False)
    description_eng = db.Column(db.String(256))
    country = db.Column(db.String(2))
    active = db.Column(db.Boolean, default=True)
    category_code_1 = db.Column(db.String(25))
    category_code_2 = db.Column(db.String(25))
    category_code_3 = db.Column(db.String(25))
    # journal_entry_lines = db.relationship('JournalEntryLine', backref='accounting_account', lazy=True)
    description_nob = db.Column(db.String(256))
    category_description_1_eng = db.Column(db.String(256))
    category_description_2_eng = db.Column(db.String(256))
    category_description_3_eng = db.Column(db.String(256))
    category_description_1_nob = db.Column(db.String(256))
    category_description_2_nob = db.Column(db.String(256))
    category_description_3_nob = db.Column(db.String(256))

    def get_url(self):
        return url_for('api.get_accounting_account', id=self.id, _external=True)

    def import_data(self, data):
        try:  # To-Do: think about feature multi-language support (more than two language).
            props = ['account_code', 'description_eng', 'description_nob', 'country', 'active', 'category_code_1',
                     'category_code_2', 'category_code_3']
            for prop in props:
                if prop in ['account_code', 'description_eng', 'description_nob', 'category_code_1', 'category_code_2',
                            'category_code_3']:
                    setattr(self, prop, escape_str(data.get(prop, getattr(self, prop))))
                else:
                    setattr(self, prop, data.get(prop, getattr(self, prop)))
            return self
        except Exception as ex:
            raise ValidationError(f'{ex.args[0]}')

    def export_data(self, lang='en'):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'account_code': self.account_code,
            'description_key': self.description_eng if lang == 'en' else self.description_nob,
            'country': self.country,
            'active': self.active,
            'category_code_1': self.category_code_1,
            'category_code_2': self.category_code_2,
            'category_code_3': self.category_code_3,
        }
