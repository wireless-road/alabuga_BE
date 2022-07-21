from datetime import datetime, date
import decimal


def to_date(dt):
    """From a date string, date object, datetime object - return a date object"""
    if isinstance(dt, str):
        return datetime.strptime(dt[:10], "%Y-%m-%d").date()
    if isinstance(dt, datetime):
        return dt.date()
    if isinstance(dt, date):
        return dt

    raise ValueError("dt must be of type str, datetime or date")


def to_amount(num, decimal_places, rounding_method=decimal.ROUND_HALF_UP):
    """
    From a numeric type or numeric str - return a Decimal amount rounded to number of decimal places.
    For NoneType values the function returns None
    """
    return (
        decimal.Decimal(num).quantize(
            decimal.Decimal("0.".ljust(decimal_places + 2, "0")),
            rounding=rounding_method,
        )
        if num is not None
        else None
    )
