import datetime
from zxcvbn import zxcvbn
from elar.common.exceptions import ValidationError


def validate_date(date_text):
    try:
        if date_text:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
            return date_text
        else:
            return date_text
    except ValueError:
        raise ValidationError(
            f"Incorrect data format {date_text}, should be YYYY-MM-DD"
        )


def validate_and_transform_date(date_text):
    validate_date(date_text)
    return datetime.datetime.strptime(date_text, "%Y-%m-%d")


def validate_integers(int_texts):
    for int_text in int_texts:
        validate_integer(int_text)


def validate_and_transform_integers(int_texts):
    return [validate_and_transform_integer(x) for x in int_texts]


def validate_integer(int_text):
    if int_text:
        if isinstance(int_text, int):
            return int_text
        elif int_text.isdigit():
            return int_text
        else:
            raise ValidationError(f"Incorrect argument {int_text}. Should be integer.")
    else:
        return int_text


def validate_and_transform_integer(int_text):
    if int_text:
        if isinstance(int_text, int):
            return int(int_text)
        elif int_text.isdigit():
            return int(int_text)
        else:
            raise ValidationError(f"Incorrect argument {int_text}. Should be integer.")
    else:
        return int_text


def validate_password(password, user_data=None):
    """Check strength of password. Uses zxcvbn, and passes a score of 3 or above."""

    if zxcvbn(password, user_data)["score"] >= 3:
        return True

    raise ValidationError("Password is too weak")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
