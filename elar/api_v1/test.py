# -*- coding: utf-8 -*-
from . import public, api
from elar.common.decorators import json
from flask import g


@public.route('/public-test/', methods=['POST'])
@json
def test_public():
    return {
        'msg': 'OK',
    }


@api.route('/token-test/', methods=['POST'])
@json
def test_token():
    return {
        'msg': 'token tested',
        'client_accounts': [account.export_data() for account in g.client_accounts],
        'len': len(g.client_accounts),
        'ids': g.client_account_ids,
    }, 200
