import logging
import functools


def cases(_cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in _cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception as err:
                    print(new_args)  # todo: change to logger
                    raise err
        return wrapper
    return decorator
