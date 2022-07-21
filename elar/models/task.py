# -*- coding: utf-8 -*-
from enum import Enum
from elar import db
from .timestamp_mixin import TimestampMixin


class RepeatUnits(Enum):
    ONETIME = "ONETIME"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"


class TaskResultTypes(Enum):
    FILE = "FILE"


class TaskNotificationMethods(Enum):
    EMAIL = "EMAIL"
    MOBILE = "MOBILE"


class TaskDefinition(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_task_definitions"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    unique_name = db.Column(db.String(50))
    description = db.Column(db.String(100))
    active_from = db.Column(db.Date)
    active_to = db.Column(db.Date)
    due_date = db.Column(db.DateTime)
    notification1_date = db.Column(db.DateTime)
    notification2_date = db.Column(db.DateTime)
    repeat_frequency = db.Column(db.Integer)
    repeat_unit = db.Column(db.String(10))


class TaskNotification(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_task_notifications"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    task_id = db.Column(
        db.BigInteger, db.ForeignKey("sb_task_definitions.id"), nullable=False
    )
    client_account_id = db.Column(
        db.BigInteger, db.ForeignKey("sb_client_accounts.id"), nullable=False
    )
    user_id = db.Column(db.BigInteger, db.ForeignKey("sb_users.id"), nullable=False)
    task_due_date = db.Column(db.DateTime)
    notification_number = db.Column(db.Integer)
    notification_method = db.Column(db.String(20))
    notification_date = db.Column(db.DateTime(timezone=True))


class TaskResult(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_task_results"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    task_id = db.Column(
        db.BigInteger, db.ForeignKey("sb_task_definitions.id"), nullable=False
    )
    client_account_id = db.Column(
        db.BigInteger, db.ForeignKey("sb_client_accounts.id"), nullable=False
    )
    task_due_date = db.Column(db.DateTime)
    result_date = db.Column(db.DateTime(timezone=True))
    result_type = db.Column(db.String(20))
    result_id = db.Column(db.BigInteger)
