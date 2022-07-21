# -*- coding: utf-8 -*-
from elar import db
from .timestamp_mixin import TimestampMixin
from flask import url_for, escape

from ..common.exceptions import ValidationError
from ..utils.utility import generate_unique_name


class ClientAccount(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_client_accounts"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    unique_name = db.Column(db.String(50), nullable=False, unique=True)
    display_name = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    accounting_currency = db.Column(db.String(3))
    organization_id = db.Column(db.BigInteger, db.ForeignKey("sb_organizations.id"))
    upload_email = db.Column(db.String(50))
    sequence_number = db.Column(db.BigInteger)
    recon_seq_num = db.Column(db.BigInteger)
    organization_number = db.Column(db.String(12))
    sale_invoice_seq_number = db.Column(db.BigInteger)
    sale_credit_notes_seq_number = db.Column(db.BigInteger)
    purchase_invoice_seq_number = db.Column(db.BigInteger)
    purchase_credit_notes_seq_number = db.Column(db.BigInteger)
    receipt_seq_number = db.Column(db.BigInteger)
    payment_seq_number = db.Column(db.BigInteger)
    accountant_notes = db.Column(db.String(100))

    # settings = db.relationship("ClientAccountSettings", backref="client_account")
    accounting_client_accounts = db.relationship(
        "ClientAccount",
        secondary="sb_contracts",
        primaryjoin="ClientAccount.id == Contract.client_account_id",
        secondaryjoin="ClientAccount.id == Contract.accounting_client_account_id",
        viewonly=True,
    )

    def get_url(self):
        return url_for("api.get_client_account", id=self.id, _external=True)

    def export_data_reduced(self):
        return {
            "self_url": self.get_url(),
            "id": self.id,
            "unique_name": self.unique_name,
            "display_name": self.display_name,
            "accounting_currency": self.accounting_currency,
            "organization": self.organization.export_data_reduced()
            if self.organization
            else None,
        }

    def export_data(self):
        return {
            "self_url": self.get_url(),
            "id": self.id,
            "unique_name": self.unique_name,
            "display_name": self.display_name,
            "accounting_currency": self.accounting_currency,
            "organization": self.organization.export_data()
            if self.organization
            else None,
        }

    def import_data(self, data):
        try:
            props = [
                "unique_name",
                "display_name",
                "upload_email",
                "organization_id",
                "organization_number",
                "accounting_currency",
                "accountant_notes"
            ]
            if "unique_name" in data:  # ['unique_name']:
                data["unique_name"] = generate_unique_name(data["unique_name"])
            for prop in props:
                if prop in [
                    "unique_name",
                    "display_name",
                    "upload_email",
                    "organization_number",
                ]:
                    setattr(self, prop, escape(data.get(prop, getattr(self, prop))))
                else:
                    setattr(self, prop, data.get(prop, getattr(self, prop)))
        except Exception as e:
            raise ValidationError(f"Invalid client account data: {e.args[0]}")
        return self
