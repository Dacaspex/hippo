
def extract(key, store, _else=None):
    return store[key] if key in store else _else


def lpad_string(string, padding_character, padding):
    result = ''
    for _ in range(padding):
        result += padding_character
    return result + string


def rpad_string(string, padding_character, padding):
    result = string
    for _ in range(padding):
        result += padding_character
    return result


def lrpad_string(string, padding_character, padding):
    return lpad_string(rpad_string(string, padding_character, padding), padding_character, padding)
