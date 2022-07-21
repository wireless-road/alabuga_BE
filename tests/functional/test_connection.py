from schlumberger import db
from schlumberger.models import User


def test_connection(create):
    with create.app_context():
        first_name = db.session.query(User.first_name).filter(User.id == 15).first()
    assert first_name[0] == 'Test'  # check if we connected to test database that has 'Test' 'Test' user with id = 15
