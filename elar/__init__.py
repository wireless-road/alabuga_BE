# -*- coding: utf-8 -*-
import os
from flask import Flask
# import firebase_admin
# from firebase_admin import credentials
from sqlalchemy.schema import MetaData
from elar.common.constants import SQLALCHEMY_NAMING_CONVENTION
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from elar.services.redis import RedisService
from flask_cors import CORS
from flask_mail import Mail
from flask_allows import Allows
# from flask_pusher import Pusher
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from elar.utils.s3_tools2 import configure_s3_client_

# import klippa_ocr_api
import logging

logger = logging.getLogger(__name__)

__version__ = "0.1.0"
metadata = MetaData(naming_convention=SQLALCHEMY_NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata)
ma = Marshmallow()
migrate = Migrate()
mail = Mail()
allows = Allows()
# pusher = Pusher()
docs = FlaskApiSpec()
limiter = Limiter(key_func=get_remote_address)
s3_client = configure_s3_client_()


# def init_klippa(app, api_key):
#     configuration = klippa_ocr_api.Configuration(
#         host="https://custom-ocr.klippa.com/api/v1", api_key={"X-Auth-Key": api_key}
#     )
#     api_client = klippa_ocr_api.ApiClient(configuration)
#     klippa_information_api = klippa_ocr_api.InformationApi(api_client)
#     klippa_parsing_api = klippa_ocr_api.ParsingApi(api_client)
#     app.klippa_information_api = klippa_information_api
#     app.klippa_parsing_api = klippa_parsing_api


# def init_firebase(app):
#     init_flag = app.config['INIT_FIREBASE']
#     if init_flag is True:
#         firebase_private_key = app.config['FIREBASE_PRIVATE_KEY'].replace(r'\n', '\n')
#         certs = {
#             'type': 'service_account',
#             'project_id': app.config['FIREBASE_PROJECT_ID'],
#             'private_key_id': app.config['FIREBASE_PRIVATE_KEY_ID'],
#             'private_key': firebase_private_key,
#             'client_email': app.config['FIREBASE_CLIENT_EMAIL'],
#             'client_id': app.config['FIREBASE_CLIENT_ID'],
#             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
#             'token_uri': 'https://oauth2.googleapis.com/token',
#             'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
#             'client_x509_cert_url': app.config['FIREBASE_CLIENT_X509_CERT_URL']
#         }
#         try:
#             cred = credentials.Certificate(certs)
#             firebase_admin.initialize_app(cred)
#         except ValueError as e:
#             logger.error(f'ERROR. Firebase initialization failed {e}')


def create_app(full_init=False) -> Flask:
    app = Flask("elar")

    CORS(app)
    config_path = "conf." + os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_path)

    app.redis = RedisService(app.config["REDIS_URI"])
    app.env = load_template_env()

    app.url_map.strict_slashes = False

    init_extensions(app)

    from worker import make_celery

    app.celery = make_celery(app)
    app.mail = mail
    # init_klippa(app, app.config["KLIPPA_API_KEY"])
    # init_firebase(app)

    if full_init:
        register_blueprints(app)

    app.config.update(
        {
            "APISPEC_SPEC": APISpec(
                openapi_version="3.0.3",
                title="Elar API",
                version="v1",
                plugins=[MarshmallowPlugin()],
            ),
        }
    )
    docs.init_app(app)

    # Trick to disable API doc generation for OPTIONS method whish annoying
    for key, value in docs.spec._paths.items():
        docs.spec._paths[key] = {
            inner_key: inner_value
            for inner_key, inner_value in value.items()
            if inner_key != "options"
        }

    return app


def init_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    allows.init_app(app)
    # pusher.init_app(app)
    limiter.init_app(app)


def register_blueprints(app: Flask):
    from elar.api_v1 import api as token_bp, login as auth_bp, public as public_bp
    from elar.api_v1 import healthy as health_check_bp

    service_name = app.config["SERVICE_NAME"]
    logger.error(f'___ service_name {service_name}')
    app.register_blueprint(token_bp, url_prefix=f"/{service_name}/api/v1")
    app.register_blueprint(auth_bp, url_prefix=f"/{service_name}/api/v1")
    app.register_blueprint(public_bp, url_prefix=f"/{service_name}/api/v1")
    app.register_blueprint(health_check_bp, url_prefix=f"/{service_name}/")


def load_template_env():
    from jinja2 import Environment, PackageLoader
    from jinja2 import select_autoescape

    env = Environment(
        loader=PackageLoader("elar", "mail_templates"),
        autoescape=select_autoescape(["html"]),
    )
    return env
