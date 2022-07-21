from elar import db
# from elar.models import TemperatureSensorMeasurement
from worker.base_task import BaseTask
import random
import logging


logger = logging.getLogger(__name__)


class TemperatureSensorTask(BaseTask):
    name = 'TemperatureSensorTask'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def run(self, sensor_id):
        logger.info('Celery. Email task started. Handling incoming emails.')
        with self.app.flask_app.app_context():
            self.log_task()
            logger.error(f'___ TemperatureSensorTask {sensor_id}')
            # new_random_measurement = TemperatureSensorMeasurement(sensor_id=sensor_id, value=random.randint(20, 28), created_by_id=1)
            # db.session.add(new_random_measurement)
            # db.session.commit()
