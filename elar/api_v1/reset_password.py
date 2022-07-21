# -*- coding: utf-8 -*-
import hashlib
import logging
from datetime import datetime
from flask import request, escape
from . import public
from elar.models.users import User
from flask import current_app as app, url_for, redirect
from flask_mail import Message
from elar import db, limiter
from urllib.parse import urlparse
from flask_apispec.annotations import doc
from elar import docs
from elar.common.constants import URI_APPENDIX


from ..common.exceptions import ValidationError
from elar.common.validations import validate_password
from ..dal.users import password_used_before
from ..models import UsedPasswords

logger = logging.getLogger(__name__)


@public.route("/reset-password", methods=["POST"])
@limiter.limit("5 per hour")
@doc(
    tags=["registration"],
    responses={
        201: {
            "description": """Password reset request handled. Verification email sent."""
        }
    },
    description="""Request to reset forgotten password using email verification.
     In a case of 'lang' argument equal to one of this values: 'nb', 'nn', 'no' Norwegian language template to be sent.
     In all other value of 'lang' argument English language template to be sent.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/reset-password
Request body example:

    {
        "email": "almaz_1c@mail.ru",
        "lang": "en"
    }""",
)
def reset_password():
    email = request.json["email"]
    lang = request.json.get("lang", "en")
    email_template = (
        "reset_password_NO.html"
        if lang in ["nb", "nn", "no"]
        else "reset_password.html"
    )
    email = email.lower().strip() if email else email
    user = User.query.filter(User.email == email).first()
    if user:
        token = user.generate_reset_password_token()
        backend_url = app.config["BACKEND_URL"]
        logger.info(
            f"reset_url:\
                    {'https://' + backend_url + URI_APPENDIX + '/reset-password/' + token}"
        )
        logger.info(f"reset password for user {user.email}, token: {token}")
        msg = Message("Reset Password", recipients=[email])

        msg.html = app.env.get_template(email_template).render(
            **{
                "reset_url": "https://"
                + backend_url
                + URI_APPENDIX
                + "/reset-password/"
                + token
            }
        )
        app.mail.send(msg)
    return {}, 201


@public.route("/reset-password-mobile", methods=["POST"])
@doc(
    tags=["registration"],
    responses={
        201: {
            "description": """Password reset request handled. Verification email sent."""
        }
    },
    description="""Request to reset forgotten password using email verification.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/reset-password-mobile
Request body example:

    {
        "email": "client@fusion-tech.pro"
    }""",
)
def reset_password_mobile():
    email = request.json["email"]
    lang = request.json.get("lang", "en")
    email_template = (
        "reset_password_mobile_NO.html"
        if lang in ["nb", "nn", "no"]
        else "reset_password_mobile.html"
    )
    email_subject = (
        "Tilbakestille passord" if lang in ["nb", "nn", "no"] else "Reset password"
    )
    email = email.lower().strip() if email else email
    user = User.query.filter(User.email == email).one_or_none()

    if not user:
        return {"status": False, "message": "User wasn't found"}, 404

    time = str(datetime.now())
    code = User.generate_reset_password_code(email=email, time=time)

    logger.info(f"reset password for user {email}, code: {code}")
    msg = Message(email_subject, recipients=[email])
    msg.html = app.env.get_template(email_template).render(**{"reset_code": f"{code}"})
    app.mail.send(msg)
    return {"status": True, "date": time, "message": "Code sent to user"}, 200


@public.route("/reset-password/<string:token>", methods=["GET"])
@doc(
    tags=["registration"],
    responses={200: {"description": """User verified."""}},
    description="""Reset password verification token URL. To be sent to user by email mesasge.
     If user calls that URL from email so password changes successfully.""",
    params={"id": {"description": "ID of message we are going to update"}},
)
def confirm_token(token):
    logger.info(f"reset-password public {request.json}")
    user = User.verify_reset_password_token(token)
    logger.info(f"user verified: {user}")
    if not user:
        raise ValidationError("invalid token")
    return {}


@public.route("/reset-password-mobile-check", methods=["POST"])
@doc(
    tags=["registration"],
    responses={200: {"description": """User verified."""}},
    description="""Reset password verification code. To be sent to user by email mesasge.
     User need to type this code in his mobile app.""",
    params={"id": {"description": "ID of message we are going to update"}},
)
def confirm_code():
    logger.info(f"reset-password public {request.json}")
    email = request.json["email"]
    email = email.lower().strip() if email else email
    user = User.query.filter(User.email == email).one_or_none()

    if not user:
        return {
            "status": False,
            "message": f"User with email {email} wasn't found",
        }, 400

    date = request.json["date"]
    candidate = request.json["code"]
    is_veryfied = user.verify_reset_password_code_mobile(
        email=email, date=date, candidate=candidate
    )

    if not is_veryfied["status"]:
        return {"status": False, "message": is_veryfied["message"]}, 401

    token = user.generate_reset_password_token()
    logger.info(f"reset password for user {user.email}, token: {token}")

    logger.info(f"user verified: {user}")
    return {"status": True, "token": token}, 200


@public.route("/new-password", methods=["POST"])
@doc(
    tags=["registration"],
    responses={201: {"description": """Password changed successfully."""}},
    description="""Request to change password. Token verification passes to change password.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/new-password
Request body example:

    {
        "password": "123321"
    }""",
    params={"id": {"description": "ID of message we are going to update"}},
)
def new_token():
    token = request.json["token"]
    password = request.json["password"]
    validate_password(password)
    password = escape(password)
    logger.info(f"reset-password public {request.json}")
    user = User.verify_reset_password_token(token)
    logger.info(f"user verified: {user}")
    if not user:
        raise ValidationError("invalid or expired token")
    user.set_password(password)
    passwordd = hashlib.sha256(password.encode()).hexdigest()
    if password_used_before(user_id=user.id, password_hash=passwordd):
        raise ValueError("ERROR. Please set password not used before.")
    used_password = UsedPasswords(
        user_id=user.id, password_hash=passwordd, created_by_id=user.id
    )
    db.session.add(user)
    db.session.add(used_password)
    db.session.commit()
    return {}


@public.route("/register-user", methods=["POST"])
@doc(
    tags=["registration"],
    responses={
        201: {
            "description": """User created. Verification email sent.""",
            "example": """{"id": 1}""",
        }
    },
    description="""Request to register user.
     Checks if user with that ID not exists yet.
     Sends email verification message to email provided in body request.
     Request URL example:

     http://localhost:5000/snapbooks/api/v1/register-user
Request body example:

    {
        "email": "almaz_1c@mail.ru",
        "first_name": "Almaz",
        "last_name": "Khamidullin",
        "password": "123321"
    }""",
    params={"id": {"description": "ID of message we are going to update"}},
)
def register_user():
    email = request.json["email"]
    email = email.lower().strip() if email else email
    logger.error(f"register-user: {email}")
    user = User.query.filter(User.email == email).first()

    if user:
        raise ValidationError("user with that e-mail already exist")

    user = User()
    user.import_data(request.json)
    logger.error(
        f"user: {user.first_name} {user.last_name} {user.email} {user.password_hash}"
    )
    user.email_verified = False
    user.created_by_id = 1
    db.session.add(user)
    db.session.commit()
    token = user.generate_register_password_token()
    logger.info(
        f"register_url: {'https://' + urlparse(request.url_root).hostname + '/register-user/' + token}"
    )
    logger.info(f"register user {user.email}, token: {token}")
    msg = Message("Email verification", recipients=[email])
    msg.html = app.env.get_template("register_user.html").render(
        **{
            "register_url": url_for(
                "public.confirm_new_user_token", token=token, _external=True
            )
        }
    )
    app.mail.send(msg)
    return {"id": user.id}, 201


@public.route("/register-user/<string:token>", methods=["GET"])
@doc(
    tags=["registration"],
    description="""Email confirmation request.
     User receives this request URL by email.
     Redirects to login page of FE in a case of valid token. It means that email verified.""",
    params={"token": {"description": "token to verify user."}},
)
def confirm_new_user_token(token):
    logger.info("register-user public")
    user = User.verify_register_user_token(token)
    logger.info(f"user: {user}")
    user.email_verified = True
    db.session.commit()
    logger.info(f"user verified: {user}")
    if not user:
        raise ValidationError("invalid token")
    return redirect("https://" + urlparse(request.url_root).hostname + "/login")


docs.register(confirm_new_user_token, blueprint="public")
docs.register(register_user, blueprint="public")
docs.register(new_token, blueprint="public")
docs.register(confirm_token, blueprint="public")
docs.register(reset_password, blueprint="public")
