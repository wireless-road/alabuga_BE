import os
from celery.app.task import Task
from celery.utils.log import get_logger
from datetime import datetime

from elar import db
from elar.models import CeleryHistory

logger = get_logger(__name__)


class BaseTask(Task):
    abstract = True
    acks_late = True
    reject_on_worker_lost = True
    ignore_result = False
    max_retries = int(os.getenv('CELERY_MAX_RETRIES_TIME', 2))
    default_retry_delay = int(os.getenv('CELERY_TIME_COUNTDOWN_RETRY', 30))
    validation_class = ''
    description = ''

    def log_task(self):
        celery_log = CeleryHistory(task_name=self.name, task_timestamp=datetime.now())
        db.session.add(celery_log)
        db.session.commit()
