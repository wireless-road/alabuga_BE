from elar import db
from flask import url_for

from elar.models import AccountingAccount
from sqlalchemy.sql.functions import concat
import logging

logger = logging.getLogger(__name__)


def query_accounting_accounts(
    client_account_id,
    page,
    base_url,
    endpoint,
    account_code=None,
    keyword=None,
    lang=None,
    only_active=None,
    per_page=25,
):
    search_query = None

    query = None
    if lang == "nb" or lang == "nn" or lang == "no":
        query = (
            db.session.query(
                AccountingAccount.account_code.label("account_code"),
                AccountingAccount.active.label("active"),
                AccountingAccount.category_code_1.label("category_1"),
                AccountingAccount.category_code_2.label("category_2"),
                AccountingAccount.category_code_3.label("category_3"),
                AccountingAccount.country.label("country"),
                AccountingAccount.description_nob.label("description_key"),
                AccountingAccount.id.label("id"),
                concat(base_url, AccountingAccount.id).label("self_url"),
            )
            .order_by(AccountingAccount.account_code)
        )
    else:
        query = (
            db.session.query(
                AccountingAccount.account_code.label("account_code"),
                AccountingAccount.active.label("active"),
                AccountingAccount.category_code_1.label("category_1"),
                AccountingAccount.category_code_2.label("category_2"),
                AccountingAccount.category_code_3.label("category_3"),
                AccountingAccount.country.label("country"),
                AccountingAccount.description_eng.label("description_key"),
                AccountingAccount.id.label("id"),
                concat(base_url, AccountingAccount.id).label("self_url"),
            )
            .order_by(AccountingAccount.account_code)
        )

    # paging
    # page = request.args.get('page', 1, type=int)
    p = query.paginate(page, per_page)
    pages = {"page": page, "per_page": per_page, "total": p.total, "pages": p.pages}
    if p.has_prev:
        pages["prev_url"] = url_for(
            endpoint, page=p.prev_num, per_page=per_page, expanded=1, _external=True
        )
    else:
        pages["prev_url"] = None
    if p.has_next:
        pages["next_url"] = url_for(
            endpoint, page=p.next_num, per_page=per_page, expanded=1, _external=True
        )
    else:
        pages["next_url"] = None
    pages["first_url"] = url_for(
        endpoint, page=1, per_page=per_page, expanded=1, _external=True
    )
    pages["last_url"] = url_for(
        endpoint, page=p.pages, per_page=per_page, expanded=1, _external=True
    )

    result2 = [r._asdict() for r in p.items]
    return {
        "accounting_accounts": result2,
    }
