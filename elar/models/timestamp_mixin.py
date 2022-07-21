# -*- coding: utf-8 -*-
from elar import db
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin(object):
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    @declared_attr
    def created_by_id(cls):
        return db.Column(db.BigInteger(), db.ForeignKey('sb_users.id'), nullable=False)

    @declared_attr
    def updated_by_id(cls):
        return db.Column(db.BigInteger(), db.ForeignKey('sb_users.id'), nullable=True)
