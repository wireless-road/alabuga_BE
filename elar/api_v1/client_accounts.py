# -*- coding: utf-8 -*-
from elar.models import ClientAccount, ClientAccountUser
from . import api
from elar.common.decorators import json, paginate
from flask import request, g
from elar import db
from flask_allows import requires
from elar.authorization import is_admin
from flask_apispec.annotations import doc
from elar import docs
import logging

from ..dal.clients import find_or_create_client_account_
from ..dal.secure_access import secure_get_client, secure_update_client

logger = logging.getLogger(__name__)


@api.route("/client-accounts/", methods=["GET"])
@doc(
    tags=["client account"],
    responses={
        200: {
            "description": """List of client accounts.""",
            "example": """{
    "client_accounts": [
        {
            "accounting_currency": "NOK",
            "display_name": "A Pluss Regnskap AS",
            "id": 16,
            "organization": {
                "address": "Sandevegen 144",
                "address2": null,
                "city": "SANDE I SUNNFJORD",
                "country": "NO",
                "departments_amount": 1,
                "id": 814783,
                "logo": null,
                "name": "A PLUSS REGNSKAP AS",
                "organization_number": "920456383",
                "parent_organization_number": null,
                "phone": null,
                "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/814783"
            },
            "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/16",
            "unique_name": "a-pluss-regnskap"
        }
    ],
    "pages": {
        "first_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/?page=1&per_page=2&expanded=1",
        "last_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/?page=6&per_page=2&expanded=1",
        "next_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/?page=2&per_page=2&expanded=1",
        "page": 1,
        "pages": 6,
        "per_page": 2,
        "prev_url": null,
        "total": 12
    }
}""",
        }
    },
    description="""Returns paginated list of client accounts.
     Client in terms of SnapBooks is any company registered n service: client and accounting companies both. 
     E.g. all companies registered in Snapbooks service.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/client-accounts?expanded=1&page=1&per_page=2
Request acceptable arguments:

    page        - paginated page number.
    per_page    - number of klippa raw lines per page.""",  # noqa = 501
)
@requires(is_admin)
@json
@paginate("client_accounts")
def get_client_accounts():
    return ClientAccount.query


@api.route("/client-accounts/<int:id>", methods=["GET"])
@doc(
    tags=["client account"],
    responses={
        200: {
            "description": """Client account information.""",
            "example": """{
    "accounting_currency": "VND",
    "display_name": "SnapBooks Corp.",
    "id": 6,
    "organization": {
        "address": null,
        "address2": null,
        "city": null,
        "country": null,
        "departments_amount": null,
        "id": 5,
        "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/Microsoft.png",
        "name": "test-microsoft",
        "organization_number": null,
        "parent_organization_number": null,
        "phone": null,
        "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/5"
    },
    "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/6",
    "unique_name": "snapbooks-corp"
}""",
        },
        404: {"description": "Company with that ID not exists."},
    },
    description="""Returns client account information.""",  # noqa = 501
    params={"id": {"description": "ID of client account we are requesting"}},
)
@json
def get_client_account(id):
    return secure_get_client(id)


@api.route("/client-accounts/<int:id>", methods=["PUT"])
@doc(
    tags=["client account"],
    responses={
        200: {
            "description": """Client account updated. Returns Company updated information.""",  # noqa = 501
            "example": """{
    "accounting_currency": "VND",
    "display_name": "SnapBooks Corp.",
    "id": 6,
    "organization": {
        "address": null,
        "address2": null,
        "city": null,
        "country": null,
        "departments_amount": null,
        "id": 5,
        "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/Microsoft.png",
        "name": "test-microsoft",
        "organization_number": null,
        "parent_organization_number": null,
        "phone": null,
        "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/5"
    },
    "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/6",
    "unique_name": "snapbooks-corp"
}""",
        },
        404: {"description": "Company with that ID not exists."},
    },  # noqa = 501
    description="""Updates client account.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/client-accounts/6
Request body example:

    {
        "upload_email": "phuc@in.snapbooks.app"
    }
""",  # noqa = 501
    params={"id": {"description": "ID of client account we are updating"}},
)
@json
def update_client_account(id):
    return secure_update_client(id, request.json)


@api.route("/client-accounts/", methods=["POST"])
@doc(
    tags=["client account"],
    responses={
        200: {
            "description": """Company account created. ID returned.""",
            "example": """{ "id": 20 }""",
        }
    },
    description="""Creates client company.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/client-accounts/
Request body example:

    {
        "display_name": "Startup Mega",
        "accounting_currency": "NOK",
        "unique_name": "Startup",
        "upload_email": "phuc@in.snapbooks.app"
    }
""",
)  # noqa = 501
@json
def create_client_account():
    account = ClientAccount(created_by_id=g.user.id)
    account.import_data(request.json)
    db.session.add(account)
    db.session.commit()
    return {"id": account.id}, 201, {"Location": account.get_url()}


@api.route("/client-accounts-users/<int:id>", methods=["PUT"])
@json
def edit_client_account_user(id):
    accountUser = ClientAccountUser.query.filter(
        ClientAccountUser.is_active == True  # noqa = 712
    ).get_or_404(id)
    accountUser.import_data(request.json)
    db.session.add(accountUser)
    db.session.commit()
    return {"id": accountUser.id}, 201


@api.route("/client-accounts-users/", methods=["POST"])
@json
def add_client_account_user():
    account_user = ClientAccountUser(created_by_id=g.user.id)
    account_user.import_data(request.json)
    account_user.is_active = True

    db.session.add(account_user)
    db.session.commit()
    return {"id": account_user.id}, 201


@api.route("/client-accounts-users/<int:id>", methods=["DELETE"])
@requires(is_admin)
@json
def delete_client_account_user(id):
    from snapbooks.models import ClientAccountUser

    ClientAccountUser.query.filter(ClientAccountUser.id == id).first().is_active = False
    db.session.commit()
    return {}, 204


@api.route("/client-accounts/find-or-create/", methods=["POST"])
@json
def find_or_create_client_account():
    return find_or_create_client_account_(request.json)


docs.register(create_client_account, blueprint="api")
docs.register(update_client_account, blueprint="api")
docs.register(get_client_account, blueprint="api")
docs.register(get_client_accounts, blueprint="api")
