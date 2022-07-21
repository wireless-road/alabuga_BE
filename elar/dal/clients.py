from elar.models import ClientAccount, ClientAccountUser, Contract
from flask import g
from elar import db
import logging

logger = logging.getLogger(__name__)


def find_or_create_client_account_(data):
    organization_number = data["organization_number"]
    client_account = (
        db.session.query(ClientAccount)
        # .join(ClientAccountUser)
        .filter(ClientAccount.organization_number == organization_number)
        # .filter(ClientAccountUser.user_id == g.user.id)
        .one_or_none()
    )

    account_exists = True if client_account else False

    if not account_exists:
        try:
            client_account = ClientAccount(created_by_id=g.user.id)
            client_account_data = {
                "unique_name": data["name"].capitalize(),
                "display_name": data["name"].capitalize(),
                "upload_email": g.user.email,
                "organization_id": data["id"],
                "organization_number": data["organization_number"],
                "accounting_currency": "NOK",
            }
            client_account.import_data(client_account_data)
            db.session.add(client_account)
            db.session.flush()
        except Exception as e:
            logger.exception(f"Can't create client account. ERROR: {e}")
            return {"message": "Can't create client account", "status": False}, 500

        account_data = {
            "user_id": g.user.id,
            "client_account_id": client_account.id,
            "role_id": 3,  # Default value
        }

        try:
            account_user = ClientAccountUser(created_by_id=g.user.id, is_active=True)
            account_user.import_data(account_data)
            db.session.add(account_user)
            db.session.flush()
        except Exception as e:
            logger.exception(
                f"Can't create relation between User and Client Account. ERROR: {e}"
            )
            return {
                "message": "Can't create relation between User and Client Account",
                "status": False,
            }, 500

        try:
            contract = Contract(
                created_by_id=g.user.id, accounting_client_account_id=18, client_account_id=client_account.id
            )
            db.session.add(contract)
            db.session.commit()
        except Exception as e:
            logger.exception(
                f"Can't create contract between Snapbooks Accounting and Client Account. ERROR: {e}"
            )
            return {
                "message": "Can't create contract between Snapbooks Accounting and Client Account",
                "status": False,
            }, 500
    else:
        logger.exception(f"Can't create client account with organization number {data['organization_number']}. Already exists")  # noqa = 501
        return {"message": f"Can't create client account with organization number {data['organization_number']}. Already exists", "status": False}, 500  # noqa = 501

    return {
        "client_account_id": client_account.id,
        "message": "Success",
        "status": True,
    }, 200 if account_exists else 201
