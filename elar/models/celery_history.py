# -*- coding: utf-8 -*-
from elar import db


class CeleryHistory(db.Model):  # type: ignore
    __tablename__: str = 'sb_celery_history'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(40), nullable=False)
    task_timestamp = db.Column(db.DateTime, nullable=False)

    def export_data(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_timestamp': self.task_timestamp
        }
