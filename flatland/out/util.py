from flatland.util import Maybe


YES = ('1', 'true', 'True', 't', 'on', 'yes')
NO = ('0', 'false', 'False', 'nil', 'off', 'no')
MAYBE = ('auto',)


def parse_trool(value):
    if value is True or value is False or value is Maybe:
        return value
    if isinstance(value, str):
        value = value.lower()
    else:
        value = str(value).lower()
    if value in YES:
        return True
    if value in NO:
        return False
    if value in MAYBE:
        return Maybe
    return Maybe
