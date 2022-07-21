# -*- coding: utf-8 -*-
import functools
import inspect
from flask import jsonify


def json(f):
    """Generate a JSON response from a database model or a Python
    dictionary."""

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # invoke the wrapped function
        rv = f(*args, **kwargs)

        # the wrapped function can return the dictionary alone,
        # or can also include a status code and/or headers.
        # here we separate all these items
        status = None
        headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status, (dict, list)):
            headers, status = status, None

        # if the response was a database model, then convert it to a
        # dictionary
        if not isinstance(rv, dict):
            _with = None
            _with_str = kwargs.get("with")
            if _with_str:
                _with = [s.strip() for s in _with_str.split(",") if s]

            rv = (
                rv.export_data(expand=_with)
                if "expand" in inspect.getfullargspec(rv.export_data).args
                else rv.export_data()
            )

        # generate the JSON response
        rv = jsonify(rv)
        if status is not None:
            rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)
        return rv

    return wrapped
