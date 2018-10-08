NAME_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
NAME_FIRST_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')

def assert_name(name: str):
    assert len(name) > 0, 'A name has to contain at least one character, got "{}"'.format(name)
    assert all(l in NAME_CHARS for l in name), 'Illegal characters in name "{}", only alphanumeric characters allowed'.format(name)
    assert name[0] in NAME_FIRST_CHARS, 'Illegal first character in name "{}", only letters are allowed as first character'.format(name)

