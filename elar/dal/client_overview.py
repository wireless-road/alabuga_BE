# -*- coding: utf-8 -*-

from elar import db
from elar.models import (
    Contract,
    ClientAccount,
)
from elar.common.exceptions import ValidationError
import logging


logger = logging.getLogger(__name__)



def get_sales(charts_new):
    sales_sum = 0
    for month in charts_new:
        if "sales" in charts_new[month]:
            sales_sum += float(charts_new[month]["sales"])
    return sales_sum


def get_accounting_companies(client_account_id):
    query = db.session.query(Contract).filter(
        Contract.client_account_id == client_account_id
    )
    data = query.all()
    return [acc.accounting_account.export_data() for acc in data]



def get_client_currency(client_account_id):
    client_currency_res = (
        db.session.query(ClientAccount.accounting_currency)
        .filter(ClientAccount.id == client_account_id)
        .first()
    )
    if client_currency_res is not None and len(client_currency_res) < 1:
        raise ValidationError("Unknown client currency")
    return client_currency_res[0]
