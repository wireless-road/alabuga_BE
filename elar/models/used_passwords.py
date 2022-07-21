from werkzeug.security import generate_password_hash
from elar import db
from .timestamp_mixin import TimestampMixin
from ..common.exceptions import ValidationError


class UsedPasswords(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_used_passwords'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('sb_users.id'))
    password_hash = db.Column(db.String(128))

    def import_data(self, data):
        try:
            self.user_id = data['user_id']
            if 'password' in data:
                self.set_password(data['password'])
        except KeyError as e:
            raise ValidationError(f'Invalid password data: {e.args[0]}')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
