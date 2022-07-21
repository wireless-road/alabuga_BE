import re

from elar.utils.string_utils import escape_norwegian_letters


def generate_unique_name(unique_name):
    res = unique_name.lower()
    res = re.sub(r"[^\w\s-]", "", res)
    res = re.sub(r"[ ]+", "-", res)
    res = re.sub(r"(-as$)|(-asa$)|(-enk$)|(-da$)|(-ans$)", "", res)
    res = escape_norwegian_letters(res)
    return res
