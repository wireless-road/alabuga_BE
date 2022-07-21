# -*- coding: utf-8 -*-
from elar import create_app
import os

import logging
logger = logging.getLogger(__name__)

app = create_app(full_init=True)


if 'SENTRY_DSN' in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        environment=os.environ.get('SENTRY_ENVIRONMENT'),
        integrations=[FlaskIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=1.0
    )

celery = app.celery
