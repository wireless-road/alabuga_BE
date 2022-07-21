# -*- coding: utf-8 -*-
from . import api
from elar.common.decorators import json
from elar.models import AccountingAccount
from elar import db
from flask import request, g
from elar.common.exceptions import ValidationError
from elar.dal.accounting_accounts import query_accounting_accounts
# from snapbooks.dal.account_suggestions import query_account_suggestions
import logging
import sys
from flask_apispec.annotations import doc
from elar import docs
from ..common.validations import validate_integer

logger = logging.getLogger(__name__)


@api.route("/accounting-accounts/<int:id>", methods=["GET"])
@doc(
    tags=["accounting accounts"],
    responses={
        200: {
            "description": """Accounting account returned.""",
            "example": """{
    "account_code": "1355",
    "active": true,
    "category_code_1": "Assets",
    "category_code_2": "13",
    "category_code_3": "",
    "country": "NO",
    "description_key": "Other units, Norwegian",
    "id": 689,
    "self_url": "http://localhost:5000/snapbooks/api/v1/accounting-accounts/689"
}""",
        },
        404: {"description": "Accounting account with given ID not exist"},
    },
    description="""Request accounting account information.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/accounting-accounts/689?expanded=1""",  # noqa = 501
    params={"id": {"description": "ID of accounting account to return."}},
)
@json
def get_accounting_account(id):
    return AccountingAccount.query.get_or_404(id)


@api.route("/accounting-accounts/", methods=["GET"])
@doc(
    tags=["accounting accounts"],
    responses={
        200: {
            "description": """Accounting accounts list returned.""",
            "example": """{
    "accounting_accounts": [
        {
            "account_code": "1000",
            "active": true,
            "category_1": "Assets",
            "category_2": "10",
            "category_3": "",
            "country": "NO",
            "description_key": "Forskning og utvikling, ervervet",
            "id": 609,
            "mandatory_dimension_results": null,
            "self_url": "http://localhost:5000/snapbooks/api/v1/accounting-accounts/609"
        }
    ]
}""",
        }
    },
    description="""Returns list of accounting accounts.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/accounting-accounts/?expanded=1&client_account_id=7&lang=no&keyword=erver
Request acceptable arguments:

    client_account_id   - company id we are looking accounting accounts to.
    lang                - language to return accounts.
    keyword             - to filter accounting accounts by search text.""",  # noqa = 501
    params={"id": {"description": "ID of message we are going to update"}},
)
@json
def get_accounting_accounts():
    client_account_id = validate_integer(request.args.get("client_account_id", None))
    if client_account_id is None:
        raise ValidationError("ERROR. client_account_id missed")

    try:
        account_code = request.args.get("account_code", None)
        keyword = request.args.get("keyword", None)
        lang = request.args.get("lang", None)
        only_active = request.args.get("only_active", True)
        page = request.args.get("page", 1, type=int)
        return query_accounting_accounts(
            client_account_id=client_account_id,
            account_code=account_code,
            keyword=keyword,
            lang=lang,
            only_active=only_active,
            page=page,
            base_url=request.base_url,
            endpoint=request.endpoint,
        )
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"query accounting accounts: line {exc_tb.tb_lineno} {ex.args[0]}")
        raise ValidationError("Error querying accounting accounts")


# @api.route("/accounting-account-suggestions/", methods=["GET"])
# @doc(
#     tags=["accounting account suggestions"],
#     responses={
#         200: {
#             "description": """Accounting account suggestion list returned.""",
#             "example": """{
#      'account_suggestions': [
#         {
#             'account_code': account_code,
#             'account_code_id': account_code_id,
#             'tax_code': tax_code,
#             'tax_code_id': tax_code_id,
#             'count': count,
#             'match_type': match_type,
#         }
#     ]
# }""",
#         }
#     },
#     description="""Returns list of suggested accounting accounts for selected document type,
#      business partner, and client, based on past documents created.
#      'count' is the number of each account_code that was previously created.
#      'match_type' is the type of match, 'client' for first level match, 'organization' for
# second level match, 'industry' for third level match.
#      First level match is the count of documents between current client and selected business
# partner for that document type.
#      Second level match is the count of documents between any client in the same industry and
# selected business partner organization for that document type.
#      Third level match is the count of documents between any client in the same industry and
# any business partner in the same industry for that document type.
#
#      Request URL example:
#
#      http://localhost:5000/snapbooks/api/v1/accounting-account-suggestions/?client_account_id=7&
# business_partner_id=11&doc_type=ARINV
#
# Request acceptable arguments:
#
#     client_account_id   - company id we are looking accounting accounts to.
#     business_partner_id - selected business partner
#     doc_type            - document type {'ARCRN', 'APCRN', 'ARINV', 'APINV', 'PAYMNT', 'RECPT', 'OTHER'}""",
#     params={"id": {"description": "ID of message we are going to update"}},
# )
# @json
# def get_accounting_account_suggestions():
#     client_account_id = validate_integer(request.args.get("client_account_id"))
#     business_partner_id = validate_integer(request.args.get("business_partner_id"))
#     doc_type = request.args.get("doc_type", None)
#
#     return query_account_suggestions(
#         client_account_id=client_account_id,
#         business_partner_id=business_partner_id,
#         doc_type=doc_type,
#     )


@api.route("/accounting-accounts/", methods=["POST"])
@doc(
    tags=["accounting accounts"],
    responses={200: {"description": """Accounting account created."""}},
    description="""Request to create accounting account.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/accounting-accounts/
Request body example:

    {
        "account_code": "13555",
        "active": true,
        "category_code_1": "Assets",
        "category_code_2": "13",
        "category_code_3": "",
        "country": "NO",
        "description_eng": "Other units, Norwegian",
        "description_nob": "Other units, Norwegian"
    }
""",  # noqa = 501
    params={"id": {"description": "ID of message we are going to update"}},
)
@json
def create_accounting_account():
    account = AccountingAccount()
    account.import_data(request.json)
    account.created_by_id = g.user.id
    db.session.add(account)
    db.session.commit()
    return {}, 201, {"Location": account.get_url()}


docs.register(create_accounting_account, blueprint="api")
docs.register(get_accounting_accounts, blueprint="api")
docs.register(get_accounting_account, blueprint="api")
# docs.register(get_accounting_account_suggestions, blueprint="api")
