from flask_allows import Requirement


class HasRole(Requirement):
    def __init__(self, role):
        self.role = role

    def fulfill(self, ctx, request):
        if isinstance(self.role, list):
            for role in self.role:
                if role in ctx.roles:
                    return True
            return False
        return self.role in ctx.roles


def is_admin(ctx):
    return ctx.user.id == 1
