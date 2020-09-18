import re
from functools import wraps
from datetime import datetime, timedelta


def type_validator(*types):
    def validator(func):
        @wraps(func)
        def wrapper(self, value):
            if not isinstance(value, types):
                t = ' or '.join((t.__name__ for t in types))
                raise TypeError(f'{self.__class__.__name__} must be {t}, not {value.__class__.__name__}')
            return func(self, value)
        return wrapper
    return validator


def email_validator(func):
    pattern = re.compile(r'^\w+@\w+\.\w+$')
    @wraps(func)
    def wrapper(self, value):
        if not re.match(pattern, str(value)):
            raise ValueError(f'{self.__class__.__name__}: {value} is not valid email')
        return func(self, value)
    return wrapper


def phone_validator(func):
    pattern = re.compile(r'^7\d{10}$')
    @wraps(func)
    @type_validator(str, int)
    def wrapper(self, value):
        if not re.match(pattern, str(value)):
            raise ValueError(f'{self.__class__.__name__}: {value} is not valid phone number')
        return func(self, value)
    return wrapper


def date_validator(fmt):
    def validator(func):
        @wraps(func)
        @type_validator(str)
        def wrapper(self, value):
            try:
                datetime.strptime(value, fmt)
            except ValueError as e:
                raise ValueError(f'{self.__class__.__name__}: {e}')
            return func(self, value)
        return wrapper
    return validator


def birthday_validator(max_years, fmt):
    def validator(func):
        @wraps(func)
        @date_validator(fmt)
        def wrapper(self, value):
            dt, now = datetime.strptime(value, fmt), datetime.now()
            if dt + timedelta(days=365 * max_years) < now:
                raise ValueError(f'{self.__class__.__name__}: age over {max_years}')
            elif dt > now:
                raise ValueError(f'{self.__class__.__name__}: {value} must be less {now.strftime(fmt)}')
            return func(self, value)
        return wrapper
    return validator
