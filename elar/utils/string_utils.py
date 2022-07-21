from flask import escape


def escape_str(text):
    if text is None:
        return None

    return escape(text)


html_escape_table = {
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}

Scandinavian_Icelandic_letters_escape_table = {
    'Á': 'A',
    'Å': 'A',
    'Æ': 'A',
    'Ó': 'O',
    'Ö': 'O',
    'Ø': 'O',
    'Ý': 'Y',
    'Þ': 'th',
    'á': 'a',
    'ã': 'a',
    'ä': 'a',
    'å': 'a',
    'æ': 'a',
    'è': 'e',
    'é': 'e',
    'ë': 'e',
    'í': 'i',
    'ð': 'd',
    'ó': 'o',
    'ö': 'o',
    'ø': 'o',
    'ú': 'u',
    'ü': 'u'
}


def escape_str_except_ampersand(text):
    if text is None:
        return None

    return "".join(html_escape_table.get(c, c) for c in text)


def escape_norwegian_letters(text):
    if text is None:
        return None

    return "".join(Scandinavian_Icelandic_letters_escape_table.get(c, c) for c in text)
