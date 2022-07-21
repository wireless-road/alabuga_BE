# -*- coding: utf-8 -*-
# flake8: noqa
from flask import Blueprint

from elar import allows
from elar.authorization import load_user_context

# password-based APIs
login = Blueprint("login", __name__)

# token-based APIs
api = Blueprint("api", __name__)

# public apis
public = Blueprint("public", __name__)

healthy = Blueprint("health_check", __name__)

allows.identity_loader(load_user_context)


from . import (
    users,
    auth,
    reset_password,
    client,
    errors,
    client_accounts,
    roles,
    test,
    contracts,
    health,
    accounting_accounts,
    # match,
    citizens
)
