# -*- coding: utf-8 -*-
'''
endpoints:
----------
    GET  /users/
    POST /users/
    GET  /users/<int:id>
    PUT  /users/<int:id>
'''
import hashlib

from elar.common.decorators import (json, paginate)
from elar.models.users import User
from elar import db
from elar.authorization import is_admin
from flask_allows import requires
from flask import request, current_app as app, g
import boto3
from uuid import uuid4
import os
from werkzeug.datastructures import FileStorage
from elar.dal.users import get_profile_info_
from . import api
import logging
from flask_apispec.annotations import doc
from elar import docs
from elar import limiter
from ..common.exceptions import ValidationError
from ..dal.secure_access import secure_get_user
from ..models import UsedPasswords

logger = logging.getLogger(__name__)


@api.route('/users/', methods=['GET'])
@doc(tags=["users"], responses={200: {'description': """Paginated ssers list returned.""",
                                      'example': """{
    "pages": {
        "first_url": "http://localhost:5000/snapbooks/api/v1/users/?page=1&per_page=2&expanded=1",
        "last_url": "http://localhost:5000/snapbooks/api/v1/users/?page=9&per_page=2&expanded=1",
        "next_url": "http://localhost:5000/snapbooks/api/v1/users/?page=2&per_page=2&expanded=1",
        "page": 1,
        "pages": 9,
        "per_page": 2,
        "prev_url": null,
        "total": 17
    },
    "users": [
        {
            "accounts": [
                {
                    "account": {
                        "accounting_currency": "NOK",
                        "display_name": "SnapBooks AS",
                        "id": 7,
                        "organization": {
                            "address": "c/o Magnus Byrkjeflot\nBjørndalen 16",
                            "address2": null,
                            "city": "BERGEN",
                            "country": "NO",
                            "departments_amount": 1,
                            "id": 757479,
                            "logo": null,
                            "name": "SNAPBOOKS AS",
                            "organization_number": "921605900",
                            "parent_organization_number": null,
                            "phone": null,
                            "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/757479"
                        },
                        "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/7",
                        "unique_name": "snapbooks"
                    },
                    "role": {
                        "created_at": "2020-10-04T11:19:14.757508+00:00",
                        "id": 3,
                        "name": "CA",
                        "self_url": "http://localhost:5000/snapbooks/api/v1/roles/3"
                    }
                }
            ],
            "contracts": [],
            "email": "snapbooks.app@gmail.com",
            "email_verified": true,
            "first_name": "Phuc",
            "id": 1,
            "last_name": "Nguyen",
            "profile_image_key": null,
            "profile_image_url": null,
            "self_url": "http://localhost:5000/snapbooks/api/v1/users/1"
        },
    ]
}"""},
                                403: {'description': 'Forbidden. Only admins allowed to get users info.'}},
     description="""Returns paginated list of users.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/users/?expanded=1&page=1&per_page=2
Request acceptable arguments:

    page        - paginated page number.
    per_page    - number of users per page.""")
@requires(is_admin)
@json
@paginate('users', max_per_page=50)
def get_users():
    return User.query


@api.route('/users/statistic/<int:id>', methods=['GET'])
@doc(tags=["users"], responses={200: {'description': """User info returned.""",
                                      'example': """{
    "accounts": [
        {
            "account": {
                "accounting_currency": "NOK",
                "display_name": "SnapBooks AS",
                "id": 7,
                "organization": {
                    "address": "c/o Magnus Byrkjeflot\nBjørndalen 16",
                    "address2": null,
                    "city": "BERGEN",
                    "country": "NO",
                    "departments_amount": 1,
                    "id": 757479,
                    "logo": null,
                    "name": "SNAPBOOKS AS",
                    "organization_number": "921605900",
                    "parent_organization_number": null,
                    "phone": null,
                    "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/757479"
                },
                "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/7",
                "unique_name": "snapbooks"
            },
            "role": {
                "created_at": "2020-10-04T11:19:14.757508+00:00",
                "id": 3,
                "name": "CA",
                "self_url": "http://localhost:5000/snapbooks/api/v1/roles/3"
            }
        }
    ],
    "contracts": [],
    "email": "snapbooks.app@gmail.com",
    "email_verified": true,
    "first_name": "Phuc",
    "id": 1,
    "last_name": "Nguyen",
    "profile_image_key": null,
    "profile_image_url": null,
    "self_url": "http://localhost:5000/snapbooks/api/v1/users/1"
}"""},
                                404: {'description': 'User with that ID not exists.'}},
     description="""Returns user info.""",
     params={"id": {"description": "ID of user to return info"}})
@json
def get_user_statistic(id):
    usr = db.session.query(User).filter(User.id == id).first()
    return usr.export_data_full()


@api.route('/users/<int:id>', methods=['GET'])
@doc(tags=["users"], responses={200: {'description': """User info returned.""",
                                      'example': """{
    "accounts": [
        {
            "account": {
                "accounting_currency": "NOK",
                "display_name": "SnapBooks AS",
                "id": 7,
                "organization": {
                    "address": "c/o Magnus Byrkjeflot\nBjørndalen 16",
                    "address2": null,
                    "city": "BERGEN",
                    "country": "NO",
                    "departments_amount": 1,
                    "id": 757479,
                    "logo": null,
                    "name": "SNAPBOOKS AS",
                    "organization_number": "921605900",
                    "parent_organization_number": null,
                    "phone": null,
                    "self_url": "http://localhost:5000/snapbooks/api/v1/organizations/757479"
                },
                "self_url": "http://localhost:5000/snapbooks/api/v1/client-accounts/7",
                "unique_name": "snapbooks"
            },
            "role": {
                "created_at": "2020-10-04T11:19:14.757508+00:00",
                "id": 3,
                "name": "CA",
                "self_url": "http://localhost:5000/snapbooks/api/v1/roles/3"
            }
        }
    ],
    "contracts": [],
    "email": "snapbooks.app@gmail.com",
    "email_verified": true,
    "first_name": "Phuc",
    "id": 1,
    "last_name": "Nguyen",
    "profile_image_key": null,
    "profile_image_url": null,
    "self_url": "http://localhost:5000/snapbooks/api/v1/users/1"
}"""},
                                404: {'description': 'User with that ID not exists.'}},
     description="""Returns user info.""",
     params={"id": {"description": "ID of user to return info"}})
@json
def get_user(id):
    logger.error(f'____ !!!!')
    return secure_get_user(user_id=id)


@api.route('/users/<int:id>/profile-image', methods=['GET'])
@doc(tags=["users"], responses={200: {'description': """User profile image URL.""",
                                      'example': """{
    "profile_image_url": "https://uploaded-docs-prod.s3.amazonaws.com/logo/29c62e16-214f-4dcd-93ea-968baba6845d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA2OWWKVZBFUEPGNUE%2F20211117%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20211117T084434Z&X-Amz-Expires=518400&X-Amz-SignedHeaders=host&X-Amz-Signature=0eb03f970f8c09f9a56b33431344a83c53b3e073ef51a143c968fda10b0dd6d1",
    "self_url": "http://localhost:5000/snapbooks/api/v1/users/22"
}"""},  # noqa = 501
                                404: {'description': 'User with that ID not exists.'}},
     description="""Returns user profile image.""",
     params={"id": {"description": "ID of user to return profile image URL"}})
def get_user_profile_image(id):
    user = secure_get_user(user_id=id)
    if type(user) is tuple:
        return user
    res = user.export_profile_image()
    return res


@api.route('/users/<int:id>', methods=['PUT'])
@doc(tags=["users"], responses={200: {'description': """User updated."""},
                                403: {'description': 'Forbidden. Only admin allowed to update user info.'},
                                404: {'description': 'User with that ID not exists.'}},
     description="""Updates user.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/user/21
Request body example:
    {
        "last_name": "Nisson"
    }
""",
     params={"id": {"description": "ID of user to upload"}})
# @requires(is_admin)
@json
def update_user(id):
    user = User.query.get_or_404(id)
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()
    return {}


@api.route('/users', methods=['PATCH'])
@doc(tags=["users"], responses={201: {'description': """User updated."""},
                                400: {'description': 'email is not valid'}},
     description="""Updates user.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/users
Request body example:

    {
        "last_name": "Jack"
        "first_name": "Smith"
        "email": "my_new_email@email.com"
    }
""")
@json
def update_me():
    allowed_fields = ['first_name', 'last_name', 'email']
    user_id = g.user.id
    user = User.query.get_or_404(user_id)
    data_to_update = {}
    for el in request.json:
        if el in allowed_fields:
            data_to_update[el] = request.json[el]

    if 'email' in data_to_update and not User.validate_email(data_to_update['email']):
        raise ValidationError("email is not valid")

    user.import_data(data_to_update)
    db.session.add(user)
    db.session.commit()
    return {"user_id": user_id,
            "message": f"User with id: {user_id}, updated successfully",
            "data": data_to_update}, 201


@api.route('/users/', methods=['POST'])
@doc(tags=["users"], responses={200: {'description': """User created. ID returned.""",
                                      'example': """{"id": 21}"""}},
     description="""Creates User.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/users/
Request body example:

    {
        "first_name": "John",
        "last_name": "Johnson",
        "email": "Jhon@company.com",
        "email_verified": "true",
        "password": "John@Johnson"
    }
""")
@json
def create_user():
    user = User()
    user.import_data(request.json)
    user.created_by_id = g.user.id
    password = request.json['password']
    passwordd = hashlib.sha256(password.encode()).hexdigest()
    db.session.add(user)
    db.session.flush()
    used_password = UsedPasswords(user_id=user.id,
                                  password_hash=passwordd,
                                  created_by_id=user.id)
    db.session.add(used_password)
    db.session.commit()
    return {"id": user.id}, 201, {'Location': user.get_url()}


@api.route('/users/profile/', methods=['GET'])
@doc(tags=["users"], responses={200: {'description': """User profile returned."""}},
     description="""Returns User profile. Currently under development.""")
@json
def get_user_profile():
    return get_profile_info_(g.user), 200


# @api.route('/users/<int:id>', methods=['DELETE'])
# @requires(is_admin)
# @json
# def delete_user(id):
#     from snapbooks.models import ClientAccountUser
#     ClientAccountUser.query.filter(ClientAccountUser.user_id == id).delete()
#     User.query.filter(User.id == id).delete()
#     db.session.commit()
#     return {}, 201


@api.route('/users/change-password/<int:id>', methods=['POST'])
@limiter.limit("10 per hour")
@doc(tags=["users"], responses={201: {'description': """Password changed successfully."""}},
     description="""Request to change password.
     Request URL example:
     http://localhost:5000/snapbooks/api/v1/users/<int:id>/change-password
    Request body example:
    g{
        "password": "123456Test"
        "new-password: "Test123456"
    }""")
def change_password(id):
    password = request.json['password']
    new_password = request.json['new_password']

    if password == new_password:
        raise ValidationError('Your new password is the same as old!')

    user = User.query.filter(User.id == id).one_or_none()
    if user is None:
        raise ValidationError('User not found')

    auth_success = user.verify_password(password)
    if not auth_success:
        logger.info(f'Invalid password for user #{id}')
        raise ValidationError('Wrong password. Try again!')
    logger.info(f'Authenticated user #{id}')

    if not User.validate_user_password(new_password):
        raise ValidationError('New password is not valid')

    user.set_password(new_password)
    db.session.add(user)
    db.session.commit()
    return {"message": "Password changed successfully."}, 201


docs.register(get_users, blueprint="api")
docs.register(get_user, blueprint="api")
docs.register(get_user_profile_image, blueprint="api")
docs.register(update_user, blueprint="api")
docs.register(update_me, blueprint="api")
docs.register(create_user, blueprint="api")
docs.register(get_user_profile, blueprint="api")
