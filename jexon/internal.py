import importlib


def __eval__(__):
    while isinstance(__, str) and len(__) > 0 and (__[0] == '!'):
        __ = eval(__[1:])
    return __


def __exec__(__):
    if isinstance(__, str) and len(__) > 0 and (__[0] == '!'):
        exec(__[1:])
