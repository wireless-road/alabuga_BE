# -*- coding: utf-8 -*-
from elar.common.exceptions import ValidationError
from elar.models import ClientAccountUser
from elar.models import User, Role


class UserManager():

    @staticmethod
    def create_client_account_user(**kwargs) -> ClientAccountUser:
        user = User.query.filter(User.email == kwargs['email']).first()
        if not user:
            raise ValidationError('Invalid user email')
        role = Role.query.filter(Role.name == kwargs['role']).first()
        if not role:
            raise ValidationError('Invalid user role')
        kwargs['user_id'] = user.id
        kwargs['role_id'] = role.id
        return ClientAccountUser.create(**kwargs)
