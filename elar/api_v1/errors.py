from flask import jsonify
from elar.common.exceptions import ValidationError, DatabaseError
from . import api, public


@api.errorhandler(ValidationError)
@public.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({"status": 400, "error": "bad request", "message": e.args[0]})
    response.status_code = 400
    return response


@api.errorhandler(DatabaseError)
@public.errorhandler(DatabaseError)
def database_system_error(e):
    response = jsonify({"status": 500, "error": "Database error", "message": e.args[0]})
    response.status_code = 500
    return response


@api.app_errorhandler(400)
@public.app_errorhandler(400)
def bad_request2(e):
    response = jsonify(
        {
            "status": 400,
            "error": "Bad Request",
            "message": (e.args[0] if e and e.args else None)
            or (e.description if hasattr(e, "description") else None)
            or "You sent a request the server could not understand.",
        }
    )
    response.status_code = 400
    return response


@api.app_errorhandler(403)
@public.app_errorhandler(403)
def forbidden(e):
    response = jsonify(
        {
            "status": 403,
            "error": "Forbidden",
            "message": "You dont have the permission to access the requested resource.",
        }
    )
    response.status_code = 403
    return response


@api.app_errorhandler(404)
@public.app_errorhandler(404)
def not_found(e):
    response = jsonify(
        {"status": 404, "error": "not found", "message": "invalid resource URI"}
    )
    response.status_code = 404
    return response


@api.errorhandler(405)
@public.errorhandler(405)
def method_not_supported(e):
    response = jsonify(
        {
            "status": 405,
            "error": "method not supported",
            "message": "the method is not supported",
        }
    )
    response.status_code = 405
    return response


@api.app_errorhandler(500)
@public.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify(
        {"status": 500, "error": "internal server error", "message": e.args[0]}
    )
    response.status_code = 500
    return response
