# -*- coding: utf-8 -*-
class ValidationError(ValueError):
    pass


class DatabaseError(Exception):
    pass


class DuplicateError(DatabaseError):
    pass


class IbanLowBalance(Exception):
    pass
