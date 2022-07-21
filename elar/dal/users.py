from elar import db
from elar.models import ClientAccountUser, ClientAccount, Organization, UsedPasswords
from elar.common.exceptions import ValidationError
import logging
import sys

logger = logging.getLogger(__name__)


def get_profile_info_(user):
    try:
        res = db.session.query(ClientAccountUser.client_account_id,
                               ClientAccount.organization_number,
                               Organization.organization_number,
                               Organization.name
                               )\
            .join(ClientAccount, ClientAccount.id == ClientAccountUser.client_account_id)\
            .outerjoin(Organization, Organization.id == ClientAccount.organization_id)\
            .filter(db.and_(ClientAccountUser.is_active == True, ClientAccountUser.user_id == user.id)).all()  # noqa = 712
        return {'user_id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'email': user.email,
                'companies': res
                }
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'user profile query error: line {exc_tb.tb_lineno} {ex.args[0]}')
        raise ValidationError('Error trying query user profile')


def password_used_before(user_id, password_hash):
    used_passwords = db.session.query(UsedPasswords).filter(db.and_(UsedPasswords.user_id == user_id,
                                                                    UsedPasswords.password_hash == password_hash)).first()  # noqa = 501
    if used_passwords is not None:
        return True
    else:
        return False
