# -*- coding: utf-8 -*-
import os
from flask import jsonify
from elar import create_app

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


@app.route('/health_check')
def health_check():
    """
    Check service health endpoint.
    """
    from sentry_sdk import configure_scope
    with configure_scope() as scope:
        if scope.transaction:
            scope.transaction.sampled = False
    return jsonify({
        'status': 'OK'
    })


@app.route('/new-password?token=<string:token>')
def new_password(token):
    return jsonify({
        'token': token
    })


@app.route('/')
def home():
    return 'Schlumberger CORE service'


if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=5000, debug=True)
