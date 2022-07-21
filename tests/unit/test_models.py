from schlumberger.models import User


def test_new_user():
    user = User(first_name='Almaz', last_name='Khamidullin')
    assert user.first_name == 'Almaz'
    assert user.last_name == 'Khamidullin'
