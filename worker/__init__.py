# -*- coding: utf-8 -*-
from celery import Celery
from flask import Flask
from .temperature_sensors import TemperatureSensorTask

CELERY_TASKS = (
    TemperatureSensorTask,
)


def make_celery(app: Flask):
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.flask_app = app
    celery.conf.update(app.config)

    class ContextTask(celery.Task):  # type: ignore
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    celery.set_default()
    for task in CELERY_TASKS:
        task.bind(celery)  # type: ignore
        celery.tasks.register(task)
    return celery
