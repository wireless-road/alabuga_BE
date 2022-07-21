# -*- coding: utf-8 -*-
import logging
from . import api
from elar.common.decorators import json
from elar.dal.client_overview import (
    get_accounting_companies,
    get_sales,
    get_client_currency,
)
from flask import g, request
from flask_apispec.annotations import doc
from elar import docs

from ..common.enums.role_enum import ROLE_CLIENT_ACCOUNT_OWNER
from elar.common.validations import validate_integer

logger = logging.getLogger(__name__)


def get_client_overview_(client_account_id):
    overview = {
        "accounting_companies": get_accounting_companies(client_account_id),
        "client_currency": get_client_currency(client_account_id),
    }

    overview["sales"] = get_sales(overview["charts_new"])
    overview["results"] = overview["sales"] - float(overview["expenses"])
    return overview


@api.route("/client/overview", methods=["GET"])
@doc(
    tags=["client"],
    responses={
        200: {
            "description": """company overview returned""",
            "example": """{
    "accounting_companies": [
        {
            "accounting_currency": "NOK",
            "display_name": "Primo Services AS",
            "id": 11,
            "organization": {
                "address": "623 Do Xuan Hop",
                "address2": null,
                "city": "Ho Chi Minh",
                "country": "NO",
                "departments_amount": null,
                "id": 10,
                "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/logo/primo-logo.jpg",
                "name": "Primo Services AS",
                "organization_number": null,
                "parent_organization_number": null,
                "phone": "0905197664",
                "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/10"
            },
            "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/11",
            "unique_name": "primo-services"
        },
        {
            "accounting_currency": "NOK",
            "display_name": "Aketo AS",
            "id": 12,
            "organization": {
                "address": "623 Do Xuan Hop",
                "address2": null,
                "city": "Ho Chi Minh",
                "country": "NO",
                "departments_amount": null,
                "id": 9,
                "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/logo/aketo-logo.jpg",
                "name": "Aketo AS",
                "organization_number": null,
                "parent_organization_number": null,
                "phone": "0905197664",
                "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/9"
            },
            "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/12",
            "unique_name": "aketo"
        }
    ],
    "accounting_questions": [
        {
            "answer_action": "ATTACH_FILE",
            "answer_options": [],
            "bank_transaction_id": null,
            "created_at": "2020-10-19T04:07:14.213715+00:00",
            "document_id": 42,
            "file_name": "My goals.pdf",
            "id": 30,
            "object_url": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/magnus@snapbooks.app/11e65417-861f-4b0f-a70c-622367ab830c.pdf",
            "question": "attach",
            "question_status": "OPEN",
            "self_url": "http://localhost:5000/snapbooks/api/v1/accounting-questions/30"
        },
        {
            "answer_action": "CHOOSE_OPTION",
            "answer_options": [
                {
                    "id": 155,
                    "option": "test answer 1",
                    "question_id": 109,
                    "selected_answer": false,
                    "self_url": "http://localhost:5000/snapbooks/api/v1/answer-options/155"
                }
            ],
            "bank_transaction_id": null,
            "created_at": "2021-02-18T20:58:33.008254+00:00",
            "document_id": 180,
            "file_name": "invoice-template-word1.png",
            "id": 109,
            "object_url": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/jorn@aketo.no/47d93d3d-4e20-4947-9914-fbe601ae1fc1.png",
            "question": "test question template 1",
            "question_status": "OPEN",
            "self_url": "http://localhost:5000/snapbooks/api/v1/accounting-questions/109"
        }
    ],
    "accounting_status": {
        "pending_document_total": 10
    },
    "bank_accounts": [
        {
            "balance": null,
            "currency": "NOK",
            "date": null,
            "estimated": 1,
            "id": 5,
            "name": "Tax account"
        }
    ],
    "charts_new": {},
    "client_currency": "NOK",
    "expenses": 0,
    "messages": [
        {
            "last_message": "Lorem ipsum dolor sit",
            "participants": [
                {
                    "email": "phuc.vinh@outlook.com"
                },
                {
                    "email": "magnus@snapbooks.app"
                }
            ],
            "thread_id": 1,
            "topic": "Sample Topic"
        }
    ],
    "payable_creditnotes": [],
    "payables": [
        {
            "business_partner_name": "Walmart",
            "currency_symbol": "USD",
            "due_date": "Mon, 07 Dec 2020 00:00:00 GMT",
            "gross_total": 46.000000,
            "logo": null,
            "posting_date": "Mon, 07 Dec 2020 00:00:00 GMT"
        },
    ],
    "receivable_creditnotes": [
        {
            "business_partner_name": "Walmart",
            "currency_symbol": "NOK",
            "due_date": "Mon, 21 Dec 2020 00:00:00 GMT",
            "gross_total": 96.000000,
            "logo": null,
            "posting_date": "Sun, 29 Nov 2020 00:00:00 GMT"
        }
    ],
    "receivables": [
        {
            "business_partner_name": "ØIVIND ANTONSEN",
            "currency_symbol": "NOK",
            "due_date": "Thu, 10 Dec 2020 00:00:00 GMT",
            "gross_total": 777.000000,
            "logo": null,
            "posting_date": "Wed, 02 Dec 2020 00:00:00 GMT"
        }
    ],
    "results": 0.0,
    "sales": 0
}""",  # noqa = 501
        },
        401: {
            "description": "request of client company information current user not eligible to get."
        },
    },
    description="""returns detailed description of company with given client_account_id.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/client/overview?client_account_id=9
Acceptable arguments:

    client_account_id - ID of company we are looking for""",
    params={"id": {"description": ""}},
)
@json
def get_client_overview():
    client_account_id = validate_integer(request.args.get("client_account_id", None))
    if not client_account_id:
        client_account_id = g.user.get_first_client_account_id(
            [ROLE_CLIENT_ACCOUNT_OWNER]
        )
    if not client_account_id:
        logger.warning("GET /client/overview: no client account id")
    return get_client_overview_(client_account_id), 200


@api.route("/client/accounting_companies", methods=["GET"])
@doc(
    tags=["client"],
    responses={
        200: {
            "description": """list of contracted accounting companies""",
            "example": """{
    "accounting_companies": [
        {
            "accounting_currency": "NOK",
            "display_name": "Primo Services AS",
            "id": 11,
            "organization": {
                "address": "623 Do Xuan Hop",
                "address2": null,
                "city": "Ho Chi Minh",
                "country": "NO",
                "departments_amount": null,
                "id": 10,
                "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/logo/primo-logo.jpg",
                "name": "Primo Services AS",
                "organization_number": null,
                "parent_organization_number": null,
                "phone": "0905197664",
                "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/10"
            },
            "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/11",
            "unique_name": "primo-services"
        },
        {
            "accounting_currency": "NOK",
            "display_name": "Aketo AS",
            "id": 12,
            "organization": {
                "address": "623 Do Xuan Hop",
                "address2": null,
                "city": "Ho Chi Minh",
                "country": "NO",
                "departments_amount": null,
                "id": 9,
                "logo": "https://uploaded-docs-staging.s3.eu-north-1.amazonaws.com/logo/aketo-logo.jpg",
                "name": "Aketo AS",
                "organization_number": null,
                "parent_organization_number": null,
                "phone": "0905197664",
                "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/9"
            },
            "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/12",
            "unique_name": "aketo"
        }
    ]
}""",
        },
        401: {
            "description": "request of client company information current user not eligible to get."
        },
    },  # noqa = 501
    description="""returns list of accounting companies cotracted with company with given client_account_id.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/client/accounting_companies?expanded=1&client_account_id=7
Acceptable arguments:

    client_account_id - ID of company we are looking for""",
)  # noqa = 501
@json
def get_client_accounting_companies():
    client_account_id = validate_integer(request.args.get("client_account_id", None))
    if not client_account_id:
        client_account_id = g.user.get_first_client_account_id(
            [ROLE_CLIENT_ACCOUNT_OWNER]
        )
    if not client_account_id:
        logger.warning("GET /client/overview: no client account id")
    accounting_companies = get_accounting_companies(client_account_id)
    return {"accounting_companies": accounting_companies}, 200


@api.route("/client/currency", methods=["GET"])
@doc(
    tags=["client"],
    responses={
        200: {
            "description": """requested client company currency.""",
            "example": """{
    "client_currency": "NOK"
}""",
        },
        401: {
            "description": "request of client company information current user not eligible to get."
        },
    },  # noqa = 501
    description="""returns client company currency. 
     Client company determined by client_account_id argument sent with request.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/client/currency?expanded=1&client_account_id=9""",  # noqa = 501
)
@json
def get_currency_of_client():
    client_account_id = validate_integer(request.args.get("client_account_id", None))
    overview = {"client_currency": get_client_currency(client_account_id)}
    return overview, 200


docs.register(get_currency_of_client, blueprint="api")
docs.register(get_client_accounting_companies, blueprint="api")
docs.register(get_client_overview, blueprint="api")
