from elar import db
from .timestamp_mixin import TimestampMixin
from flask import url_for

from ..common.exceptions import ValidationError


class Calendar(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_calendar'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)

    def get_url(self):
        return url_for('api.get_calendar', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'date': self.date
        }

    def import_data(self, data):
        try:
            self.date = data['date']
        except KeyError as e:
            raise ValidationError(f'Invalid contract data: {e.args[0]}')
