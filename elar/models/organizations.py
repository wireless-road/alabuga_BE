# -*- coding: utf-8 -*
from typing import Iterable
from elar.utils.string_utils import escape_str
from elar import db
from .timestamp_mixin import TimestampMixin
from flask import url_for

from ..common.exceptions import ValidationError


class Organization(TimestampMixin, db.Model):  # type: ignore
    __tablename__: str = "sb_organizations"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    address2 = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    province = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(2), nullable=True)
    postal = db.Column(db.String(100), nullable=True)
    longitude = db.Column(db.Float(), nullable=True)
    latitude = db.Column(db.Float(), nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    organization_number = db.Column(db.String(12))
    accounts = db.relationship("ClientAccount", backref="organization", lazy=True)
    vat_liable = db.Column(db.Boolean, nullable=True)
    industrial_classification_local = db.Column(db.String(20), nullable=True)
    business_entity_type = db.Column(db.String(20), nullable=True)
    url = db.Column(db.String(1000), nullable=True)
    departments_amount = db.Column(db.BigInteger, nullable=True)
    parent_organization_number = db.Column(db.String(20), nullable=True)
    number_of_employees = db.Column(db.Integer)
    incorporation_date = db.Column(db.Date)
    registration_date = db.Column(db.Date)
    liquidation_date = db.Column(db.Date)
    deletion_date = db.Column(db.Date)
    __table_args__ = (
        db.Index(
            "organization_name_gin_idx",
            name,
            postgresql_using="gin",
            postgresql_ops={
                "name": "gin_trgm_ops",
            },
        ),
        db.Index(
            "idx_organization_number", organization_number, postgresql_using="btree"
        ),
    )

    # def get_url(self):
    #     return url_for("api.get_organization", id=self.id, _external=True)

    def export_data_reduced(self):
        return {
            # "self_url": self.get_url(),
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": "",
            "address2": "",
            "city": self.city,
            "country": self.country,
            "logo": self.logo,
            "organization_number": self.organization_number,
            "parent_organization_number": self.parent_organization_number,
        }

    def export_data(self, expand: Iterable[str] = []):
        return {
            # "self_url": self.get_url(),
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "address2": self.address2,
            "city": self.city,
            "country": self.country,
            "logo": self.logo,
            "organization_number": self.organization_number,
            "parent_organization_number": self.parent_organization_number,
            "departments_amount": self.departments_amount,
        }

    def export_data_address_only(self):
        return {
            "address": self.address,
            "city": self.city,
            "country": self.country,
        }

    def import_data(self, data):
        try:
            props = [
                "address",
                "address2",
                "name",
                "city",
                "phone",
                "country",
                "logo",
                "organization_number",
                "parent_organization_number",
                "number_of_employees",
                "incorporation_date",
                "registration_date",
                "liquidation_date",
                "deletion_date",
            ]
            for prop in props:
                if prop in [
                    "address",
                    "address2",
                    "city",
                    "phone",
                    "logo",
                    "organization_number",
                    "parent_organization_number",
                ]:
                    setattr(
                        self,
                        prop,
                        escape_str(data.get(prop, getattr(self, prop))),
                    )
                else:
                    setattr(self, prop, data.get(prop, getattr(self, prop)))
        except KeyError as e:
            raise ValidationError(f"Invalid Organization: missing {e.args[0]}")
        except Exception:
            raise ValidationError("Invalid Organization data")
        return self
