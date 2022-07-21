# -*- coding: utf-8 -*-
import functools
import inspect
from flask import url_for, request


def paginate(collection, max_per_page=25):
    """Generate a paginated response for a resource collection.

    Routes that use this decorator must return a SQLAlchemy query as a
    response.

    The output of this decorator is a Python dictionary with the paginated
    results. The application must ensure that this result is converted to a
    response object, either by chaining another decorator or by using a
    custom response object that accepts dictionaries."""

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # invoke the wrapped function
            query = f(*args, **kwargs)

            # obtain pagination arguments from the URL's query string
            page = request.args.get("page", 1, type=int)
            per_page = min(
                request.args.get("per_page", max_per_page, type=int), max_per_page
            )
            expanded = None
            if request.args.get("expanded", 1, type=int) != 0:
                expanded = 1

            _with = None
            _with_str = request.args.get("with", None, type=str)
            if _with_str:
                _with = [s.strip() for s in _with_str.split(",") if s]

            # run the query with Flask-SQLAlchemy's pagination
            p = query.paginate(page, per_page)

            # new kwargs without params already read from request
            kwargs_unique = {
                k: kwargs[k]
                for k in kwargs
                if k not in ["page", "per_page", "expanded", "with"]
            }

            # build the pagination metadata to include in the response
            pages = {
                "page": page,
                "per_page": per_page,
                "total": p.total,
                "pages": p.pages,
            }
            if p.has_prev:
                pages["prev_url"] = url_for(
                    request.endpoint,
                    page=p.prev_num,
                    per_page=per_page,
                    expanded=expanded,
                    _external=True,
                    **kwargs_unique
                )
            else:
                pages["prev_url"] = None
            if p.has_next:
                pages["next_url"] = url_for(
                    request.endpoint,
                    page=p.next_num,
                    per_page=per_page,
                    expanded=expanded,
                    _external=True,
                    **kwargs_unique
                )
            else:
                pages["next_url"] = None
            pages["first_url"] = url_for(
                request.endpoint,
                page=1,
                per_page=per_page,
                expanded=expanded,
                _external=True,
                **kwargs_unique
            )
            pages["last_url"] = url_for(
                request.endpoint,
                page=p.pages,
                per_page=per_page,
                expanded=expanded,
                _external=True,
                **kwargs_unique
            )

            # generate the paginated collection as a dictionary
            if expanded:
                results = [
                    item.export_data(expand=_with)
                    if "expand" in inspect.getfullargspec(item.export_data).args
                    and _with
                    else item.export_data()
                    for item in p.items
                ]
            else:
                results = [item.get_url() for item in p.items]

            # return a dictionary as a response
            return {collection: results, "pages": pages}

        return wrapped

    return decorator


def get_paginate(query, max_per_page=25):
    # obtain pagination arguments from the URL's query string
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", max_per_page, type=int), max_per_page)
    # run the query with Flask-SQLAlchemy's pagination
    p = query.paginate(page, per_page)

    # build the pagination metadata to include in the response
    pages = {"page": page, "per_page": per_page, "total": p.total, "pages": p.pages}
    if p.has_prev:
        pages["prev_url"] = url_for(
            request.endpoint,
            page=p.prev_num,
            per_page=per_page,
            expanded=1,
            _external=True,
        )
    else:
        pages["prev_url"] = None
    if p.has_next:
        pages["next_url"] = url_for(
            request.endpoint,
            page=p.next_num,
            per_page=per_page,
            expanded=1,
            _external=True,
        )
    else:
        pages["next_url"] = None
    pages["first_url"] = url_for(
        request.endpoint, page=1, per_page=per_page, expanded=1, _external=True
    )
    pages["last_url"] = url_for(
        request.endpoint, page=p.pages, per_page=per_page, expanded=1, _external=True
    )
    return pages, p.items
