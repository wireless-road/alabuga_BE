# -*- coding: utf-8 -*-
"""
auth.py
-------
Authentication APIs.
"""

# from datetime import datetime, timedelta
from datetime import datetime, timedelta
import logging
import urllib.parse

from flask.helpers import make_response

from elar.common.exceptions import ValidationError
from . import api as api_bp, login as login_bp
from . import public
from flask import g, jsonify, current_app, request, url_for
from elar.models import User
from sqlalchemy import func
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from elar.common.decorators import json
from elar.dal.managers import ClientAccountManager
from elar.models import ClientAccountUser
from flask_apispec.annotations import doc
from elar import db, limiter
from elar.common.validations import validate_integer, validate_password

logger = logging.getLogger(__name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@public.route("/auth/test-email", methods=["POST"])
@limiter.limit("50 per hour")
@json
def email_test():
    """
    Test if user with this email exist in system
    """
    email = request.json.get("email")
    email = email.lower().strip() if email else email
    g.user = User.query.filter(User.email == email).one_or_none()

    if g.user:
        return {
            "message": f"User with email {email} already exist",
            "status": False,
        }, 400

    return {"message": "success", "status": True}, 200


@api_bp.route("/auth/verify-token", methods=["GET"])
@limiter.limit("50 per hour")
@json
def verify_token():
    """
    Verify token
    """
    return {"user": g.user.export_data(), "message": "Token verifyed successfully"}, 200


@public.route("/auth/signup", methods=["POST"])
@limiter.limit("50 per hour")
@doc(
    tags=["bank accounts"],
    responses={
        201: {"description": """new user account created""", "example": """{}"""},
        404: {"description": ""},
    },
    description="""adds new user account.
     Request URL example:
     http://localhost:5000/snapbooks/api/v1/auth/signup/
    Request body example:
     {
        "email": "user@mail.com",
        "password": "password",
        "email_verified": "true"
    }
    """,
)  # noqa = 501
@json
def signup_user():
    first_name = request.json.get("firstname")
    if first_name is None or first_name == "":
        raise ValidationError("ERROR. Empty first name not allowed")
    last_name = request.json.get("lastname")
    if last_name is None or last_name == "":
        raise ValidationError("ERROR. Empty last name not allowed")

    email = request.json.get("email")
    email = email.lower().strip() if email else email
    password = request.json.get("password")
    if password is None or password == "":
        raise ValidationError("ERROR. Empty password not allowed")
    token_expires_seconds = current_app.config["TOKEN_EXPIRE_TIME"]

    email_verified = request.json.get("email_verified")
    user = False

    if verify_password(email, password):
        user = User.query.filter(User.email == email).one_or_none()
    elif User.query.filter(User.email == email).one_or_none():
        return {"message": f"Wrong password for user {email}", "status": False}, 400

    # If user already exists
    if user:
        object_to_continue = {
            "message": f"User with email {email} already exist",
            "require": "client_account",
            "client_account_id": None,
            "token": user.generate_auth_token(expires_in=token_expires_seconds),
            "user": user.export_data(),  # return user
            "status": False,
        }
        # Test on client account
        client_account_user = ClientAccountUser.query.filter(
            ClientAccountUser.user_id == user.id
        ).first()
        if not client_account_user:
            return object_to_continue, 200
        client_account_id = client_account_user.client_account_id
        # Test on bank account
        # bank_account = BankAccount.query.filter(
        #     BankAccount.client_account_id == client_account_id
        # ).first()
        # if not bank_account:
        #     object_to_continue["require"] = "bank_account"
        #     object_to_continue["client_account_id"] = client_account_id
        #     return object_to_continue, 200

        # Trigger signup event handler
        # SignupEventTask().delay(user.id)

        return (
            {
                "message": f"User with email {email} already exist and registrated. \
                 Move to the application to continue",
                "token": user.generate_auth_token(expires_in=token_expires_seconds),
                "user": user.export_data(),
                "status": True,
            },
            200,
        )

    if not validate_password(password, email):
        raise ValidationError("The password is too weak")

    # Create user
    try:
        g.user = User(first_name=first_name, last_name=last_name, email=email)
        g.user.set_password(password)
        g.user.created_by_id = 1
        g.user.email_verified = email_verified
        db.session.add(g.user)
        db.session.commit()
    except Exception as e:
        logger.error({"Catch exception": e})
        return {"message": "Error saving user", "status": False}, 500

    # Trigger signup event handler
    # SignupEventTask().delay(g.user.id)

    return {
        "token": g.user.generate_auth_token(expires_in=token_expires_seconds),
        "user": g.user.export_data(),
        "status": True,
        "message": "User created succesfully",
    }, 201


@api_bp.before_request
@token_auth.login_required
def before_request():
    """
    All routes in api blueprint require token-based authentication.
    """
    pass


@api_bp.after_request
def after_request(rv):
    """
    Generate an ETag header for all routes in this blueprint.
    """
    return rv


@login_bp.route("/auth/login", methods=["GET", "POST"])
@basic_auth.login_required
def get_auth_token():
    """
    Get user authentication token. User need to provide username and password.
    """
    client_id = request.args.get("client_id", None)

    token_expires_seconds = current_app.config["TOKEN_EXPIRE_TIME"]
    refresh_token_expires_seconds = current_app.config["REFRESH_TOKEN_EXPIRE_TIME"]

    response = None
    if client_id == "mobile":
        # Return access token, refresh token and user information in response body
        response = make_response(
            {
                "token": g.user.generate_auth_token(expires_in=token_expires_seconds),
                "refresh_token": g.user.generate_refresh_token(
                    expires_in=refresh_token_expires_seconds
                ),
                "user": g.user.export_data(client_id),
            }
        )
    else:
        # Return access token and user information in response body
        response = make_response(
            {
                "token": g.user.generate_auth_token(expires_in=token_expires_seconds),
                "user": g.user.export_data(client_id),
            }
        )
        # Create refresh token as cookie for the refresh-token endpoint
        response.set_cookie(
            "refresh_token",
            g.user.generate_refresh_token(expires_in=refresh_token_expires_seconds),
            timedelta(seconds=refresh_token_expires_seconds),
            expires=datetime.now() + timedelta(seconds=refresh_token_expires_seconds),
            path=urllib.parse.urlparse(
                url_for("login.refresh_token", _external=True)
            ).path,
            secure=not current_app.testing,
            httponly=True,
            samesite="Strict",
        )

    # LoginEventTask().delay(g.user.id)

    return response


@login_bp.route("/auth/refresh-token", methods=["POST"])
@json
def refresh_token():
    """
    Get renewed authentication token.
    """
    client_id = request.args.get("client_id", None)

    token = request.cookies.get("refresh_token")
    if not token and request.headers.get("Authorization"):
        token = request.headers.get("Authorization").split()[1]
    if not token or not verify_refresh_token(token):
        return {"message": "Invalid refresh token"}, 401

    token_expires_seconds = current_app.config["TOKEN_EXPIRE_TIME"]
    return {
        "token": g.user.generate_auth_token(expires_in=token_expires_seconds),
        "user": g.user.export_data(client_id),
    }


@api_bp.route("/auth/logout", methods=["POST"])
def user_logout():
    current_app.redis.deny_token(g.auth_token)
    response = jsonify({"status": 200, "message": g.auth_token})
    response.delete_cookie(
        "refresh_token",
        path=urllib.parse.urlparse(url_for("login.refresh_token", _external=True)).path,
    )
    response.status_code = 200
    return response


def verify_password_(email, password):
    email = email.lower().strip() if email else email
    if not email:
        return False
    if not password:
        return False
    g.user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    if g.user is None:
        return False
    auth_success = g.user.verify_password(password)
    if auth_success:
        logger.info(f"Authenticated user {email}")
    else:
        logger.info(f"Invalid login {email}")
    return auth_success is True


@basic_auth.verify_password
def verify_password(email, password):
    """
    Authenticate username/password.
    """
    email = email.lower().strip() if email else email
    return verify_password_(email, password)


@basic_auth.error_handler
def unauthorized():
    response = jsonify(
        {"status": 401, "error": "unauthorized", "message": "please authenticate"}
    )
    response.status_code = 401
    return response


@token_auth.verify_token
def verify_auth_token(auth_token):
    if current_app.config.get("IGNORE_AUTH") is True:
        g.user = User.query.get(1)
    else:
        if current_app.redis.is_token_denied(auth_token):
            return False
        g.user = User.verify_auth_token(auth_token)
        g.auth_token = auth_token
        if g.user:
            g.client_accounts = ClientAccountManager.get_client_accounts_by_user_id(
                g.user.id
            )
            g.client_account_ids = [
                client_account.id for client_account in g.client_accounts
            ]
            g.client_account_id = validate_integer(
                request.args.get("client_account_id", None)
            )
            g.contracts = g.user.export_contracts()
            eligible_client_account_id = []
            for account in g.client_accounts:
                eligible_client_account_id.append(account.id)
            for contract in g.contracts:
                eligible_client_account_id.append(contract)
            g.eligible_clients = eligible_client_account_id
            client_account_id = validate_integer(
                request.args.get("client_account_id", type=int)
            )
            if (
                client_account_id
                and client_account_id not in eligible_client_account_id
            ):
                logger.info(
                    "g.user: "
                    + str(g.user.id)
                    + " "
                    + str(g.user.first_name)
                    + " "
                    + str(g.user.last_name)
                    + "eligible_client_account_id: "
                    + str(eligible_client_account_id)
                    + "client_account_id: "
                    + str(client_account_id)
                )
                return False
    return g.user is not None


def verify_refresh_token(refresh_token):
    if current_app.redis.is_token_denied(refresh_token):
        return False
    g.user = User.verify_refresh_token(refresh_token)
    g.auth_token = refresh_token
    if g.user:
        g.client_accounts = ClientAccountManager.get_client_accounts_by_user_id(
            g.user.id
        )
        g.client_account_ids = [
            client_account.id for client_account in g.client_accounts
        ]
        g.client_account_id = validate_integer(
            request.args.get("client_account_id", None)
        )
        g.contracts = g.user.export_data().get("contracts")
        eligible_client_account_id = []
        for account in g.client_accounts:
            eligible_client_account_id.append(account.id)
        for contract in g.contracts:
            eligible_client_account_id.append(contract["client_account_id"])
        g.eligible_clients = eligible_client_account_id
        client_account_id = validate_integer(
            request.args.get("client_account_id", type=int)
        )
        if client_account_id and client_account_id not in eligible_client_account_id:
            logger.info(
                "g.user: "
                + str(g.user.id)
                + " "
                + str(g.user.first_name)
                + " "
                + str(g.user.last_name)
                + "eligible_client_account_id: "
                + str(eligible_client_account_id)
                + "client_account_id: "
                + str(client_account_id)
            )
            return False

    return g.user is not None


@token_auth.error_handler
def unauthorized_token():
    response = jsonify(
        {
            "status": 401,
            "error": "unauthorized",
            "message": "please send your authentication token",
        }
    )
    response.status_code = 401
    return response


def get_eligible_clients(client_account_id):
    g.client_accounts = ClientAccountManager.get_client_accounts_by_user_id(g.user.id)
    g.client_account_ids = [client_account.id for client_account in g.client_accounts]
    g.client_account_id = client_account_id
    g.contracts = g.user.export_data().get("contracts")
    eligible_client_account_id = []
    for account in g.client_accounts:
        eligible_client_account_id.append(account.id)
    for contract in g.contracts:
        eligible_client_account_id.append(contract["client_account_id"])
    g.eligible_clients = eligible_client_account_id
    return eligible_client_account_id
