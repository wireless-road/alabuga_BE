# -*- coding: utf-8 -*-
from flask_allows import requires
from sqlalchemy.sql.functions import concat

from elar.models import Contract, ClientAccount
from . import api
from elar.common.decorators import json
from flask import request, g
from elar import db
# from flask_allows import requires
# from snapbooks.authorization import is_admin
from flask_apispec.annotations import doc
from elar import docs
from sqlalchemy.orm import aliased

from ..authorization import is_admin
from ..dal.secure_access import secure_get_contract, secure_update_contract


@api.route('/contracts/', methods=['GET'])
@doc(tags=["contracts"], responses={200: {'description': """Paginated list of contracts returned.""",
                                          'example': """{
    "contracts": [
        {
            "accounting_client_account_id": 16,
            "client_account_id": 8,
            "id": 7,
            "self_url": "http://localhost:5000/snapbooks/api/v1/contracts/7"
        },
        {
            "accounting_client_account_id": 17,
            "client_account_id": 9,
            "id": 8,
            "self_url": "http://localhost:5000/snapbooks/api/v1/contracts/8"
        }
    ],
    "pages": {
        "first_url": "http://localhost:5000/snapbooks/api/v1/contracts/?page=1&per_page=2&expanded=1",
        "last_url": "http://localhost:5000/snapbooks/api/v1/contracts/?page=4&per_page=2&expanded=1",
        "next_url": "http://localhost:5000/snapbooks/api/v1/contracts/?page=2&per_page=2&expanded=1",
        "page": 1,
        "pages": 4,
        "per_page": 2,
        "prev_url": null,
        "total": 8
    }
}"""}},
     description="""Returns paginated list of contracts.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/contracts/?expanded=1&page=1&per_page=2
Request acceptable arguments:

    page     - number of paginated page to return.
    per_page - number of contracts per page.""")  # noqa = 501
@requires(is_admin)
def get_contracts():
    company1 = aliased(ClientAccount)
    company2 = aliased(ClientAccount)
    res = db.session.query(Contract.id,
                           Contract.accounting_client_account_id,
                           Contract.client_account_id,
                           company1.unique_name.label('accountant_name'),
                           company2.unique_name.label('client_name'),
                           company2.organization_number.label('client_organizaton_number'),
                           company2.accounting_currency.label('client_currency'),
                           concat(company2.unique_name, 'in.snapbooks.app').label('client_email'))\
        .join(company1, company1.id == Contract.accounting_client_account_id)\
        .join(company2, company2.id == Contract.client_account_id).all()
    return {'contracts': res}


@api.route('/contracts/<int:id>', methods=['GET'])
@doc(tags=["contracts"], responses={200: {'description': """Contract information returned.""",
                                          'example': """{
    "accounting_client_account_id": 11,
    "client_account_id": 8,
    "id": 1,
    "self_url": "http://localhost:5000/snapbooks/api/v1/contracts/1"
}
"""},
                                    404: {'description': """Contract with that ID not found."""}},
     description="""Returns contract information.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/contracts/1?expanded=1""",  # noqa = 501
     params={"id": {"description": "ID of contract we are requestion information for"}})
@json
def get_contract(id):
    return secure_get_contract(id)


@api.route('/contracts/<int:id>', methods=['PUT'])
@doc(tags=["contracts"], responses={200: {'description': """Contract edited. Returns contract state after editing.""",
                                          'example': """{
    "accounting_client_account_id": 11,
    "client_account_id": 8,
    "id": 1,
    "self_url": "http://localhost:5000/snapbooks/api/v1/contracts/1"
}"""},
                                    400: {'description': 'Not provided accounting_client_account_id or client_account_id'}},  # noqa = 501
     description="""Updates contract information: accounting client id or client id.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/contracts/1
Request body example:

    {
        "accounting_client_account_id" : 11,
        "client_account_id" : 8
    }
Here **accounting_client_account_id** is accounting company id contracted with **client_account_id** client company.""",  # noqa = 501
     params={"id": {"description": "ID of message we are going to update"}})
@json
def put_contract(id):
    return secure_update_contract(id=id, data=request.json)


@api.route('/contracts/', methods=['POST'])
@doc(tags=["contracts"], responses={201: {'description': """Contract created. It's ID returned.""",
                                          'example': """{
    "id": 13
}"""}},
     description="""Request to create contract between client company and accounting company.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/contracts/
Request body example:

    {
        "accounting_client_account_id" : 11,
        "client_account_id" : 8
    }
""")  # noqa = 501
@json
def post_contract():
    contract = Contract(created_by_id=g.user.id)  # To-do: add check if such contract already exists.
    contract.import_data(request.json)
    db.session.add(contract)
    db.session.commit()
    return {'id': contract.id}, 201, {'Location': contract.get_url()}


# @api.route('/contracts/<int:id>', methods=['DELETE'])
# @doc(tags=["contracts"], responses={204: {'description': """Contract deleted"""},
#                                     403: {'description': 'Only admin allowed to delete contract.'}},
#      description="""Request to delete contract.
#      Request URL exaple:
#
#      http://localhost:5000/snapbooks/api/v1/contracts/13?expanded=1""",  # noqa = 501
#      params={"id": {"description": "ID of contract we are requesting to delete"}})
# @requires(is_admin)
# @json
# def delete_contract(id):
#     Contract.query.filter(Contract.id == id).delete()
#     db.session.commit()
#     return {}, 204


# docs.register(delete_contract, blueprint="api")
docs.register(post_contract, blueprint="api")
docs.register(put_contract, blueprint="api")
docs.register(get_contract, blueprint="api")
docs.register(get_contracts, blueprint="api")
