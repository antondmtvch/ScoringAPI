import re
import datetime
from functools import update_wrapper

__all__ = ['type_validator', 'email_validator', 'phone_validator', 'date_validator']


def decorator(deco):
    def wrapped(f):
        return update_wrapper(deco(f), f)
    update_wrapper(wrapped, deco)
    return wrapped


@decorator
def type_validator(*types):
    def validator(func):
        def wrapper(self, value):
            if not isinstance(value, types):
                t = ' or '.join((t.__name__ for t in types))
                raise TypeError(f'{self.__class__.__name__} must be {t}, not {value.__class__.__name__}')
            return func(self, value)
        return wrapper
    return validator


@decorator
def email_validator(func):
    pattern = re.compile(r'^\w+@\w+\.\w+$')

    def wrapper(self, value):
        if not re.match(pattern, str(value)):
            raise ValueError(f'{self.__class__.__name__}: {value} is not valid email')
        return func(self, value)
    return wrapper


@decorator
def phone_validator(func):
    pattern = re.compile(r'^7\d{10}$')

    def wrapper(self, value):
        if not re.match(pattern, str(value)):
            raise ValueError(f'{self.__class__.__name__}: {value} is not valid phone number')
        return func(self, value)
    return wrapper


@decorator
def date_validator(fmt):
    def validator(func):
        def wrapper(self, value):
            try:
                datetime.datetime.strptime(value, fmt)
            except ValueError as e:
                raise e
            return func(self, value)
        return wrapper
    return validator
