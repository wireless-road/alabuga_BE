from flask import g
from sqlalchemy import func
from elar import db
from elar.common.exceptions import ValidationError
from elar.models import (
    ClientAccountUser,
    User,
    ClientAccount,
    Contract,
)
import logging

logger = logging.getLogger(__name__)


def res_404():
    return {"error": "not found", "message": "invalid resource URI", "status": 404}, 404


def res_403():
    return {
        "error": "not allowed",
        "message": "illegal resource URI",
        "status": 403,
    }, 403


def secure_get_user(user_id):
    eligible_clients = set(g.eligible_clients)
    # logger.error(f'___ eligible_clients {eligible_clients}')

    res = (
        db.session.query(User, func.json_agg(ClientAccountUser.client_account_id))
        .outerjoin(ClientAccountUser, ClientAccountUser.user_id == User.id)
        .filter(User.id == user_id)
        .group_by(User.id)
        .first()
    )  # return example: (<User jorn@aketo.no>, [12])

    if res is None:
        return res_404()

    clients = set(res[1])
    intersection = eligible_clients.intersection(clients)

    if len(intersection) == 0:
        return res_403()

    return res[0]


def secure_get_clients_list():
    eligible_clients = g.eligible_clients
    res = db.session.query(ClientAccount).filter(ClientAccount.id.in_(eligible_clients))
    return res


def secure_get_client(id):
    eligible_clients = set(g.eligible_clients)

    res = db.session.query(ClientAccount).filter(ClientAccount.id == id).first()

    if res is None:
        return res_404()

    if id not in eligible_clients:
        return res_403()

    return res


def secure_get_client_(id):
    eligible_clients = set(g.eligible_clients)

    res = db.session.query(ClientAccount).filter(ClientAccount.id == id).first()

    if res is None:
        return None, res_404()

    if id not in eligible_clients:
        return None, res_403()

    return res, None


def secure_update_client(id, data):
    instance, msg = secure_get_client_(id)
    if instance is None:
        return msg
    instance.import_data(data)
    db.session.add(instance)
    db.session.commit()
    return instance.export_data()


def secure_get_contract(id):
    eligible_clients = set(g.eligible_clients)

    res = db.session.query(Contract).filter(Contract.id == id).first()

    if res is None:
        return res_404()

    if (
        res.client_account_id not in eligible_clients
        and res.accounting_client_account_id not in eligible_clients
    ):
        return res_403()
    return res


def secure_get_contract_(id):
    eligible_clients = set(g.eligible_clients)

    res = db.session.query(Contract).filter(Contract.id == id).first()

    if res is None:
        return None, res_404()

    if (
        res.client_account_id not in eligible_clients
        and res.accounting_client_account_id not in eligible_clients
    ):
        return None, res_403()
    return res, None


def secure_update_contract(id, data):
    instance, msg = secure_get_contract_(id)
    if instance is None:
        return msg

    instance.import_data(data)
    db.session.add(instance)
    db.session.commit()
    return instance.export_data()


def secure_get(resource, id, active_only=False):
    eligible_clients = set(g.eligible_clients)

    if active_only is True:
        res = db.session.query(resource).filter(resource.id == id).filter(resource.is_active == True).first()  # noqa
    else:
        res = db.session.query(resource).filter(resource.id == id).first()

    if res is None:
        return res_404()

    if res.client_account_id not in eligible_clients:
        return res_403()
    return res


def filter_query(query, resource, filters):
    if filters:
        for arg in filters:
            query = query.filter(getattr(resource, arg) == filters[arg])
    return query


def secure_get_list(resource, client_account_id=None, filters=None, active_only=False):
    eligible_clients = g.eligible_clients
    if client_account_id:
        if client_account_id not in eligible_clients:
            raise ValidationError('Illegal request to resources')
        else:
            query = db.session.query(resource).filter(resource.client_account_id == client_account_id)
            if filters: query = filter_query(query, resource, filters)  # noqa = 701
            if active_only is True:
                query = query.filter(resource.is_active == True)  # noqa
            return query
    query = db.session.query(resource).filter(resource.client_account_id.in_(eligible_clients))
    if filters: query = filter_query(query, resource, filters)  # noqa = 701
    if active_only is True:
        query = query.filter(resource.is_active == True)  # noqa
    return query


# def secure_get_files(client_account_id=None):
#     query = secure_get_list(UploadedFile, client_account_id)
#     query = query.filter(db.and_(UploadedFile.is_active == True, UploadedFile.ignore_flag != True))  # noqa = 206
#     return query


def secure_get_(resource, id):
    eligible_clients = set(g.eligible_clients)

    res = db.session.query(resource).filter(resource.id == id).first()
    if res is None:
        return None, res_404()

    if res.client_account_id not in eligible_clients:
        return None, res_403()
    return res, None


def secure_update(resource, id, data):
    instance, msg = secure_get_(resource, id)
    if instance is None:
        return msg

    instance.import_data(data)
    db.session.add(instance)
    db.session.commit()
    return instance.export_data()
