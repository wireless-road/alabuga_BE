# -*- coding: utf-8 -*-
from elar.models import Citizens
from . import api
from elar.common.decorators import json, paginate
from flask import request, g
from elar import db
from flask_apispec.annotations import doc
from elar import docs
from ..common.exceptions import ValidationError
from ..common.validations import validate_and_transform_integer
from ..dal.secure_access import secure_get, secure_update, secure_get_list
from ..models import Citizens


@api.route('/citizens/', methods=['GET'])
@json
@paginate('citizens')
def get_citizens():
    client_account_id = validate_and_transform_integer(request.args.get('client_account_id', None))
    if client_account_id is None:
        raise ValidationError('client_account_id missed')
    return secure_get_list(Citizens, client_account_id)


@api.route('/citizens/<int:id>', methods=['GET'])
@json
def get_citizen(id):
    return secure_get(Citizens, id)


@api.route('/citizens/<int:id>', methods=['PUT'])
@json
def update_citizen(id):
    return secure_update(resource=Citizens, id=id, data=request.json)


@api.route('/citizens/', methods=['POST'])
@json
def create_citizen():
    project = Citizens(created_by_id=g.user.id)
    project.import_data(request.json)
    db.session.add(project)
    db.session.commit()
    return {'id': project.id}, 201, {'Location': project.get_url()}

docs.register(create_citizen, blueprint="api")
docs.register(update_citizen, blueprint="api")
docs.register(get_citizen, blueprint="api")
docs.register(get_citizens, blueprint="api")
