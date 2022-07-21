# -*- coding: utf-8 -*-
import logging
import hashlib
import re
from datetime import datetime
from typing import Iterable
from elar.utils.string_utils import escape_str
from flask import current_app, url_for
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    SignatureExpired,
    BadSignature,
)
from werkzeug.security import generate_password_hash, check_password_hash
from elar import db
from .contracts import Contract
from .timestamp_mixin import TimestampMixin
from elar.common.exceptions import ValidationError
from ..utils.s3_tools import create_presigned_url

logger = logging.getLogger(__name__)


class User(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_users"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(length=50), nullable=True)
    last_name = db.Column(db.String(length=50), nullable=True)
    email = db.Column(db.String(length=120), index=True)
    email_verified = db.Column(db.Boolean, default=False)
    profile_image_url = db.Column(db.String(256), nullable=True)
    profile_image_key = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(length=24), nullable=True)
    last_login_date = db.Column(db.DateTime(timezone=True), nullable=True)
    failed_login_attempt_counter = db.Column(db.Integer(), nullable=True)
    failed_login_attempt_counter_date = db.Column(db.DateTime, nullable=True)
    reset_password_counter = db.Column(db.Integer, nullable=True)
    reset_password_counter_date = db.Column(db.DateTime, nullable=True)

    EXPIRES_IN = 3600  # time expires in seconds

    client_accounts = db.relationship(
        "ClientAccount",
        secondary="sb_client_account_users",
        primaryjoin="User.id == ClientAccountUser.user_id",
        secondaryjoin="ClientAccount.id == ClientAccountUser.client_account_id",
        viewonly=True,
    )

    def get_url(self):
        return url_for("api.get_user", id=self.id, _external=True)

    def get_first_client_account_id(self, roles=None):
        from elar.models import ClientAccountUser, Role

        query = ClientAccountUser.query
        if roles:
            query = query.join(
                Role,
                db.and_(Role.id == ClientAccountUser.role_id, Role.name.in_(roles)),
            )
        query = query.filter(
            db.and_(
                ClientAccountUser.is_active.is_(True),
                ClientAccountUser.user_id == self.id,
            )
        )  # noqa = 712
        rows = query.all()
        first_row = next(iter(rows), None)
        return first_row.client_account_id if first_row else None

    def export_data_reduced(self):
        from elar.models import ClientAccountUser

        user_accounts = ClientAccountUser.query.filter(
            db.and_(
                ClientAccountUser.is_active.is_(True),
                ClientAccountUser.user_id == self.id,
            )
        ).all()  # noqa = 712, 501
        contracts = Contract.query.filter(
            Contract.accounting_client_account_id.in_(
                [user_account.account.id for user_account in user_accounts]
            )
        )
        return {
            "self_url": self.get_url(),
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "email_verified": self.email_verified,
            "accounts": [
                {
                    "account": user_account.account.export_data_reduced(),
                    "role": user_account.role.export_data_reduced(),
                }
                for user_account in user_accounts
            ],
            "contracts": [
                {
                    "contract_id": c.id,
                    "client_account_id": c.client_account.id,
                    "unique_name": c.client_account.unique_name,
                    "display_name": c.client_account.display_name,
                    "accounting_currency": c.client_account.accounting_currency,
                }
                for c in contracts
            ],
        }

    def export_contracts(self, app=None):
        from elar.models import ClientAccountUser

        user_accounts = ClientAccountUser.query.filter(
            ClientAccountUser.user_id == self.id
        ).all()
        user_accounts_ = [user_account.account.id for user_account in user_accounts]
        isclient = False
        if user_accounts:
            isclient = user_accounts[0].role_id == 3
        ress = None
        if app == "mobile" or isclient:
            ress = (
                db.session.query(Contract.client_account_id)
                .filter(Contract.client_account_id.in_(user_accounts_))
                .all()
            )  # noqa = 501
        else:
            ress = (
                db.session.query(Contract.client_account_id)
                .filter(Contract.accounting_client_account_id.in_(user_accounts_))
                .all()
            )  # noqa = 501
        res = [x[0] for x in ress]
        return res

    # old version of export_data() function. Slow.
    def export_data_old(self, app=None):
        from elar.models import ClientAccountUser

        account = "accounting_client_account_id"
        user_accounts = ClientAccountUser.query.filter(
            ClientAccountUser.user_id == self.id
        ).all()
        isclient = False
        if user_accounts:
            isclient = user_accounts[0].role_id == 3
        if app == "mobile" or isclient:
            account = "client_account_id"
        contracts = Contract.query.filter(
            getattr(Contract, account).in_(
                [user_account.account.id for user_account in user_accounts]
            )
        )
        logger.error(f"___ cnt {len(contracts.all())}")
        return {
            "self_url": self.get_url(),
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "email_verified": self.email_verified,
            "profile_image_url": self.profile_image_url,
            "profile_image_key": self.profile_image_key,
            "accounts": [
                {
                    "id": user_account.id,
                    "account": user_account.account.export_data(),
                    "role": user_account.role.export_data(),
                }
                for user_account in user_accounts
            ],
            "contracts": [
                {
                    "contract_id": c.id,
                    "client_account_id": c.client_account.id,
                    "unique_name": c.client_account.unique_name,
                    "display_name": c.client_account.display_name,
                    "accounting_currency": c.client_account.accounting_currency,
                    "upload_email": c.client_account.upload_email,
                }
                for c in contracts
            ],
        }

    # new version of export_data() function. Faster.
    def export_data(self, app=None, expand: Iterable[str] = ["accounts", "contracts"]):
        from elar.models import ClientAccountUser, ClientAccount

        user_accounts = ClientAccountUser.query.filter(
            ClientAccountUser.user_id == self.id
        ).all()
        user_accounts_ = [user_account.account.id for user_account in user_accounts]
        isclient = False
        if user_accounts:
            isclient = user_accounts[0].role_id == 3
        if app == "mobile" or isclient:
            contracts = (
                db.session.query(Contract, ClientAccount)
                .join(ClientAccount, Contract.client_account_id == ClientAccount.id)
                .filter(Contract.client_account_id.in_(user_accounts_))
            )
        else:
            contracts = (
                db.session.query(Contract, ClientAccount)
                .join(ClientAccount, Contract.client_account_id == ClientAccount.id)
                .filter(Contract.accounting_client_account_id.in_(user_accounts_))
            )

        res = {
            "self_url": self.get_url(),
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "email_verified": self.email_verified,
            "profile_image_url": create_presigned_url(
                bucket_name=current_app.config["UPLOAD_DOC_S3_BUCKET"],
                object_name=self.profile_image_key,
                expiration=518400,  # can't be higher that 7 days
            )
            if self.profile_image_key
            else None,
        }

        if not expand or ("accounts" in expand and user_accounts):
            res["accounts"] = [
                {
                    "id": user_account.id,
                    "account": user_account.account.export_data(),
                    "role": user_account.role.export_data(),
                }
                for user_account in user_accounts
            ]

        if not expand or ("contracts" in expand and contracts):
            res["contracts"] = [
                {
                    "contract_id": c[0].id,
                    "client_account_id": c[1].id,
                    "unique_name": c[1].unique_name,
                    "display_name": c[1].display_name,
                    "accounting_currency": c[1].accounting_currency,
                    "upload_email": c[1].upload_email,
                    "accountant_notes": c[1].accountant_notes
                }
                for c in contracts
            ]

        return res

    def export_profile_image(self):
        res = {
            "self_url": self.get_url(),
            "profile_image_url": create_presigned_url(
                bucket_name=current_app.config["UPLOAD_DOC_S3_BUCKET"],
                object_name=self.profile_image_key,
                expiration=518400,  # can't be higher that 7 days
            )
            if self.profile_image_key
            else None,
        }
        return res

    def is_accountant(self):
        from elar.models import ClientAccountUser

        user_accounts = ClientAccountUser.query.filter(
            ClientAccountUser.user_id == self.id
        ).all()
        for user_account in user_accounts:
            isaccountant = user_account.role_id == 2
            if isaccountant:
                return True
        return False

    def export_data_full(self):
        from elar.models import ClientAccountUser

        user_accounts = ClientAccountUser.query.filter(
            db.and_(
                ClientAccountUser.is_active.is_(True),
                ClientAccountUser.user_id == self.id,
            )
        ).all()  # noqa = 712, 501
        contracts = Contract.query.filter(
            Contract.accounting_client_account_id.in_(
                [user_account.account.id for user_account in user_accounts]
            )
        )
        return {
            "self_url": self.get_url(),
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "email_verified": self.email_verified,
            "profile_image_url": self.profile_image_url,
            "profile_image_key": self.profile_image_key,
            # 'phone': self.phone,
            "accounts": [
                {
                    "account": user_account.account.export_data(),
                    "role": user_account.role.export_data(),
                }
                for user_account in user_accounts
            ],
            "contracts": [
                {
                    "contract_id": c.id,
                    "client_account_id": c.client_account.id,
                    "unique_name": c.client_account.unique_name,
                    "display_name": c.client_account.display_name,
                    "accounting_currency": c.client_account.accounting_currency,
                    "upload_email": c.client_account.upload_email,
                    "organization": c.client_account.organization.export_data(),
                }
                for c in contracts
            ],
        }

    def import_data(self, data):
        try:
            props = [
                "first_name",
                "last_name",
                "email",
                "profile_image_url",
                "profile_image_key",
            ]  # , 'phone']
            for prop in props:
                if prop in [
                    "first_name",
                    "last_name",
                    "email",
                    "profile_image_url",
                    "profile_image_key",
                ]:
                    setattr(self, prop, escape_str(data.get(prop, getattr(self, prop))))
                else:
                    setattr(self, prop, data.get(prop, getattr(self, prop)))
            if "password" in data:
                self.set_password(data["password"])
            if "email_verified" in data:
                self.email_verified = str(data["email_verified"]).lower() in [
                    "true",
                    "yes",
                    "y",
                    "1",
                    "verified",
                ]
        except KeyError as e:
            raise ValidationError(f"Invalid customer: missing {e.args[0]}")
        return self

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def validate_user_password(password):
        """
        Validate user password. Rules:
        At least 8 characters long;
        Includes 1 uppercase and 1 lowercase letter;
        Include 1 number;
        """
        val = True

        if len(password) < 8:
            logger.info("length should be at least 8")
            val = False

        if not any(char.isdigit() for char in password):
            logger.info("Password should have at least one numeral")
            val = False

        if not any(char.isupper() for char in password):
            logger.info("Password should have at least one uppercase letter")
            val = False

        if not any(char.islower() for char in password):
            logger.info("Password should have at least one lowercase letter")
            val = False

        if val:
            return val

    def validate_email(email):
        return bool(
            re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email)
        )

    def generate_auth_token(self, expires_in=3600):
        """
        Generate auth token for this user.
        """
        logger.info(
            f"Generate auth token user {self.email}, expired in {expires_in} seconds."
        )
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_in)
        tmp = {
            "user_id": self.id,
            "email_verified": self.email_verified,
            "token_type": "access_token",
        }
        return s.dumps(tmp).decode("utf-8")

    def generate_refresh_token(self, expires_in=3600):
        """
        Generate refresh token for this user.
        """
        logger.info(
            f"Generate refresh token user {self.email}, expired in {expires_in} seconds."
        )
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_in)
        tmp = {
            "user_id": self.id,
            "email_verified": self.email_verified,
            "token_type": "refresh_token",
        }
        return s.dumps(tmp).decode("utf-8")

    def generate_register_password_token(self, expires_in=3600):
        """
        Generate register-password token for this user.
        """
        logger.info(
            f"Generate register-password token user {self.email}, expired in {expires_in} seconds."
        )
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_in)
        return s.dumps({"register_password": self.id}).decode("utf-8")

    def generate_reset_password_token(self, expires_in=10800):
        """
        Generate reset-password token for this user.
        """
        logger.info(
            f"Generate reset-password token user {self.email}, expired in {expires_in} seconds."
        )
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_in)
        return s.dumps({"reset_password": self.id}).decode("utf-8")

    @classmethod
    def generate_reset_password_code(self, email, time):
        """
        Generate 4 digit reset-password code for this user.
        """
        string = f"{email}{time}{current_app.config['SECRET_KEY']}"
        code = str(
            int(hashlib.sha1(string.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
        )[0:4]
        logger.info(
            f"Generate reset-password code for user {email}, expired in {self.EXPIRES_IN} seconds."
        )
        return code

    @classmethod
    def verify_reset_password_code_mobile(self, email, date, candidate):
        """
        Verify reset-password code for this user.
        """
        string = f"{email}{date}{current_app.config['SECRET_KEY']}"
        code = str(
            int(hashlib.sha1(string.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
        )[0:4]

        if code != str(candidate):
            logger.info(f"Generate reset-password code for user {email} is wrong")
            return {
                "status": False,
                "message": f"Generated reset-password code for user {email} is wrong",
            }
        current_time = datetime.now()
        candidate_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        difference = current_time - candidate_time
        minutes, seconds = divmod(
            difference.days * 24 * 60 * 60 + difference.seconds, 60
        )

        if minutes * 60 + seconds > self.EXPIRES_IN:
            logger.info(
                f"Generate reset-password code for user {email}, expired in {self.EXPIRES_IN} seconds."
            )
            return {
                "status": False,
                "message": f"Generated reset-password code for user {email},\
             expired in {self.EXPIRES_IN} seconds.",
            }
        return {"status": True}

    @staticmethod
    def verify_auth_token(token):
        """
        verify auth token, load data from db to g.
        """
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            if data["email_verified"] is not True:
                raise ValidationError("Unverified email address")
            if data["token_type"] != "access_token":
                raise ValidationError("Not an access token")
            return User.query.get(data["user_id"])
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except Exception:
            return None
        return None

    @staticmethod
    def verify_refresh_token(token):
        """
        verify refresh token, load data from db to g.
        """
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            if data["email_verified"] is not True:
                raise ValidationError("Unverified email address")
            if data["token_type"] != "refresh_token":
                raise ValidationError("Not a refresh token")
            return User.query.get(data["user_id"])
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except Exception:
            return None
        return None

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            assert data["reset_password"] > 0
            return User.query.get(data["reset_password"])
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except Exception:
            return None
        return None

    @staticmethod
    def verify_register_user_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            assert data["register_password"] > 0
            return User.query.get(data["register_password"])
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except Exception:
            return None
        return None
