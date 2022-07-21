from datetime import datetime
from logging import INFO

import pytest
from schlumberger import create_app, db
from schlumberger.models import (
    Contract,
    ClientAccount,
    ClientAccountUser
)
from sqlalchemy import text


@pytest.fixture(scope="session")
def create():
    flask_app = create_app(True)
    flask_app.logger.setLevel(level=INFO)
    flask_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
        flask_app.config["DB_USER"],
        flask_app.config["DB_PASSWORD"],
        flask_app.config["DB_HOST_INTEGRATION_TEST"],
        flask_app.config["DB_PORT"],
        flask_app.config["DB_NAME"],
    )
    flask_app.config["SERVER_NAME"] = "localhost:3000"
    # register_blueprints(flask_app)

    with flask_app.app_context():
        connection = db.engine.connect()
        query = "BEGIN work; ALTER TABLE locker ADD COLUMN lock_flag integer;"
        connection.execute(text(query))  # noqa: 101

    # return flask_app
    yield flask_app

    with flask_app.app_context():
        today = datetime.utcnow().strftime("%Y-%m-%d")
        db.session.query(Contract).filter(Contract.created_at >= today).delete(
            synchronize_session=False
        )
        db.session.query(ClientAccountUser).filter(ClientAccountUser.created_at >= today).delete(
            synchronize_session=False
        )
        db.session.query(ClientAccount).filter(ClientAccount.created_at >= today).delete(
            synchronize_session=False
        )

        query = "ALTER TABLE locker DROP COLUMN lock_flag; COMMIT work;"
        connection.execute(text(query))  # noqa: 101
