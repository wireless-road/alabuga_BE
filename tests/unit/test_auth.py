from schlumberger.common.validations import validate_password
from schlumberger.common.exceptions import ValidationError
import pytest


def test_password_validation():

    # Check that no digits throw error
    with pytest.raises(ValidationError):
        validate_password("QsikdoSk")

    # Check that no characters throw error
    with pytest.raises(ValidationError):
        validate_password("84652913")

    # Check that less than 8 chars throw error
    with pytest.raises(ValidationError):
        validate_password("A9k.-d!")

    # Check that password from dictionary throw error
    with pytest.raises(ValidationError):
        validate_password("Password123?")

    # Check that good password doesnt throw error
    assert (
        validate_password("Really long and 2 good password with 8 symbols...-!!@?")
        is True
    )
