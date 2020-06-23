
def extract(key, store, _else=None):
    return store[key] if key in store else _else
