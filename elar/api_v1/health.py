
from . import healthy
from flask_apispec.annotations import doc
from elar import docs


@healthy.route('/health_check', methods=['GET'])
@doc(tags=["health check"], responses={200: {'description': """Service is healthy.""",
                                             'example': """ { 'status': 'OK' }"""}},
     description="""URL used to check health of backend.
     Request URL example:
     
     https://staging.snapbooks.app/snapbooks/health_check
Doesn't need autorization token to be provided.""")  # noqa = 501
def health_check():
    """
    Check service health endpoint.
    """
    from sentry_sdk import configure_scope
    with configure_scope() as scope:
        if scope.transaction:
            scope.transaction.sampled = False
    return {
        'status': 'OK'
    }


docs.register(health_check, blueprint="health_check")
