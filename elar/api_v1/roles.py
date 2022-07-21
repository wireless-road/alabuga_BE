# -*- coding: utf-8 -*-
from . import api
from elar.common.decorators import (json, paginate)
from elar.models import Role
from flask import request, g
from elar import db
from flask_apispec.annotations import doc
from elar import docs


@api.route('/roles/', methods=['GET'])
@doc(tags=["roles"], responses={200: {'description': """Returns list of roles.""",
                                      'example': """{
    "pages": {
        "first_url": "http://localhost:5000/snapbooks/api/v1/roles/?page=1&per_page=2&expanded=1",
        "last_url": "http://localhost:5000/snapbooks/api/v1/roles/?page=3&per_page=2&expanded=1",
        "next_url": "http://localhost:5000/snapbooks/api/v1/roles/?page=2&per_page=2&expanded=1",
        "page": 1,
        "pages": 3,
        "per_page": 2,
        "prev_url": null,
        "total": 5
    },
    "roles": [
        {
            "created_at": "2020-10-04T11:19:06.315140+00:00",
            "id": 1,
            "name": "SA",
            "self_url": "http://localhost:5000/snapbooks/api/v1/roles/1"
        }
    ]
}"""},
                                404: {'description': ''}},
     description="""Returns list of roles.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/roles/?expanded=1&page=1&per_page=2
Each user in SnapBooks has role:

    CA - client account
    AA - accountant account
    BK - bookkeeper
    SA - system admin
    EM - Employee
     """)  # noqa = 501
@json
@paginate('roles')
def get_roles():
    return Role.query


@api.route('/roles/<int:id>', methods=['GET'])
@doc(tags=["roles"], responses={200: {'description': """Role returned.""",
                                      'example': """{
    "created_at": "2020-10-04T11:19:06.315140+00:00",
    "id": 1,
    "name": "SA",
    "self_url": "http://localhost:5000/snapbooks/api/v1/roles/1"
}"""},
                                404: {'description': 'Role with that ID not exists.'}},
     description="""Returns role.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/roles/1?expanded=1""",  # noqa = 501
     params={"id": {"description": "ID of role to get"}})
@json
def get_role(id):
    return Role.query.get_or_404(id)


@api.route('/roles/<int:id>', methods=['PUT'])
@doc(tags=["roles"], responses={200: {'description': """Role updated."""},
                                404: {'description': 'Role with that ID not exists.'}},
     description="""Updates Role.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/roles/6
Request body example:

    {
        "name": "EE"
    }
""",  # noqa = 501
     params={"id": {"description": "ID of roles to update"}})
@json
def update_role(id):
    role = Role.query.get_or_404(id)
    role.import_data(request.json)
    role.updated_by_id = g.user.id
    db.session.add(role)
    db.session.commit()
    return {}


@api.route('/roles/', methods=['POST'])
@doc(tags=["roles"], responses={201: {'description': """Role created. ID returned.""",
                                      'example': """{"id": 6}"""}},
     description="""Creates role.
     Request URL example:
     
     http://localhost:5000/snapbooks/api/v1/roles/
Request body example:

    {
        "name": "EU"
    }""")  # noqa = 501
@json
def create_role():
    role = Role(created_by_id=g.user.id)
    role.import_data(request.json)
    db.session.add(role)
    db.session.commit()
    return {'id': role.id}, 201, {'Location': role.get_url()}


docs.register(create_role, blueprint="api")
docs.register(update_role, blueprint="api")
docs.register(get_role, blueprint="api")
docs.register(get_roles, blueprint="api")
