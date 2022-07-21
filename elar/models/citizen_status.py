# -*- coding: utf-8 -*-
import logging
import hashlib
import re
from datetime import datetime
from typing import Iterable
from elar.utils.string_utils import escape_str
from flask import current_app, url_for
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    SignatureExpired,
    BadSignature,
)
from werkzeug.security import generate_password_hash, check_password_hash
from elar import db
from .contracts import Contract
from .timestamp_mixin import TimestampMixin
from elar.common.exceptions import ValidationError
from ..utils.s3_tools import create_presigned_url

logger = logging.getLogger(__name__)


class CitizenStatus(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_citizen_statuses"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=50), nullable=True)
    # citizen = db.relationship("CitizenStatus", back_populates="status", lazy=True)
    # citizen = db.relationship("Citizen", back_populates="citizen", lazy=True)
    # measurements = db.relationship(
    #     "TemperatureSensorMeasurement",
    #     backref="temperature_sensor",
    #     lazy=True,
    #     cascade="all, delete-orphan",
    # )



    def get_url(self):
        return url_for("api.get_citizen", id=self.id, _external=True)

    def export_data(self, expand_measurements=True):
        export = {
            'self_url': self.get_url(),
            'id': self.id,
            'name': self.name,
            # 'surname': self.surname,
            # 'age': self.age,
            # 'salary': self.salary
            # 'client_account_id': self.client_account_id,
        }
        # if expand_measurements:
        #     export["measurements"] = [
        #         line.export_data(expand_temperature_sensor=False)
        #         for line in self.measurements
        #     ]
        return export


    def import_data(self, data):
        try:
            self.name = data['name']
            # self.client_account_id = data['client_account_id']
        except KeyError as e:
            raise ValidationError(f'Invalid status data: {e.args[0]}')

    def __repr__(self):
        return f"<CitStatus {self.id}>"

