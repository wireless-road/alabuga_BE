# -*- coding: utf-8 -*-
import logging
from flask import g


logger = logging.getLogger(__name__)


class UserContext(dict):
    def __init__(self, user, roles, permissions):
        super(UserContext, self).__init__(_user=user, _roles=roles, _permissions=permissions or {})
        logger.info(f'init UserContext {user} {roles} {permissions}')

    @property
    def user(self):
        return self.get('_user')

    @property
    def roles(self):
        return self.get('_roles')

    @property
    def permissions(self):
        return self.get('_permissions')


def load_user_context():
    roles = []
    permissions = {}
    return UserContext(
        user=g.user,
        roles=roles,
        permissions=permissions
    )
