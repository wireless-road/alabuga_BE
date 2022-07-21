# -*- coding: utf-8 -*-
from elar import db
from .timestamp_mixin import TimestampMixin
import enum
from flask import url_for

from ..common.exceptions import ValidationError


class RoleEnum(enum.Enum):
    """
    sys admin
    accountant - account owner
    client - account owner
    bookkeeper
    employee
    """
    SA = 1
    AA = 2
    CA = 3
    BK = 4
    EM = 5


class Role(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = 'sb_roles'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(2), nullable=False)

    def get_url(self):
        return url_for('api.get_role', id=self.id, _external=True)

    def export_data_reduced(self):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'name': self.name
            # 'created_at': self.created_at.isoformat(),
        }

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
        }

    def import_data(self, data):
        try:
            props = [
                'name',
            ]
            for prop in props:
                setattr(self, prop, data.get(prop, getattr(self, prop)))
        except KeyError as e:
            raise ValidationError(f'Invalid role: {e.args[0]}')
        return self

    def __repr__(self):
        return f'<Role {self.name}>'
