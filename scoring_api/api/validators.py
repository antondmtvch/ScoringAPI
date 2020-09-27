import re
from functools import wraps
from datetime import datetime, timedelta
from scoring_api.api.exceptions import ValidationError

__all__ = ['type_validator', 'email_validator', 'phone_validator', 'date_validator']


def type_validator(func):
    @wraps(func)
    def wrapper(self, value):
        if not isinstance(value, self.types):
            t = ' or '.join((t.__name__ for t in self.types))
            raise ValidationError(f'{repr(self.name)} must be {t}, not {value.__class__.__name__}')
        return func(self, value)
    return wrapper


def email_validator(func):
    pattern = re.compile(r'^[._\w]+@\w+\.\w{2,10}$')
    @wraps(func)
    def wrapper(self, value):
        if not re.match(pattern, value):
            raise ValidationError(f'{value} is not valid email')
        return func(self, value)
    return wrapper


def phone_validator(func):
    pattern = re.compile(r'^7\d{10}$')
    @wraps(func)
    def wrapper(self, value):
        if not re.match(pattern, str(value)):
            raise ValidationError(f'{value} is not valid phone number')
        return func(self, value)
    return wrapper


def date_validator(fmt):
    def validator(func):
        @wraps(func)
        def wrapper(self, value):
            try:
                self.parsed_date = datetime.strptime(value, fmt)
            except ValueError:
                raise ValidationError(f'invalid date format for {repr(self.name)} field, expected {fmt}')
            return func(self, value)
        return wrapper
    return validator
