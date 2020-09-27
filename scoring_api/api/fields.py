import abc
from weakref import WeakKeyDictionary
from datetime import datetime, timedelta

from scoring_api.api.exceptions import ValidationError
from scoring_api.api.validators import email_validator, type_validator, phone_validator, date_validator


UNKNOWN, MALE, FEMALE = 0, 1, 2

GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class BaseField(abc.ABC):
    default = ''
    types = (str,)

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        if value is None:
            self.data[instance] = self.default
        else:
            self.data[instance] = value

    def __set_name__(self, owner, name):
        self.name = name

    def validate(self, value):
        if value == self.default or value is None:
            if self.required:
                if not self.nullable:
                    raise ValidationError(f'field {repr(self.name)} is required')
            elif not self.nullable:
                raise ValidationError(f'field {repr(self.name)} not be nullable')
        else:
            self.validate_value(value)

    @abc.abstractmethod
    def validate_value(self, value): pass


class CharField(BaseField):
    types = (str,)

    @type_validator
    def validate_value(self, value): pass


class EmailField(CharField):

    @type_validator
    @email_validator
    def validate_value(self, value): pass


class PhoneField(CharField):
    types = (str, int)

    @type_validator
    @phone_validator
    def validate_value(self, value):
        try:
            instance, _ = next(self.__dict__['data'].items())
            self.data[instance] = str(value)
        except StopIteration:
            pass


class ArgumentsField(BaseField):
    default = {}
    types = (dict,)

    @type_validator
    def validate_value(self, value): pass


class DateField(CharField):
    dt_format = '%d.%m.%Y'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parsed_date = None

    def _post_validate(self, value):
        try:
            instance, _ = next(self.__dict__['data'].items())
            self.data[instance] = self.parsed_date
        except StopIteration:
            pass

    @type_validator
    @date_validator(dt_format)
    def validate_value(self, value):
        self._post_validate(value)


class BirthDayField(DateField):
    dt_format = '%d.%m.%Y'
    max_years = 70

    @type_validator
    @date_validator(dt_format)
    def validate_value(self, value):
        current_time = datetime.now()
        if self.parsed_date + timedelta(days=365 * self.max_years) < current_time:
            raise ValidationError(f'invalid value for {repr(self.name)} field, age over {self.max_years}')
        elif self.parsed_date > current_time:
            str_fmt = current_time.strftime(self.dt_format)
            raise ValidationError(f'invalid value for {repr(self.name)} field, value must be less {str_fmt}')
        self._post_validate(value)


class GenderField(BaseField):
    types = (int,)

    @type_validator
    def validate_value(self, value):
        if value not in GENDERS.keys():
            raise ValidationError(f'{repr(self.name)} field value must be 0 or 1 or 2, not {value}')


class ClientIDsField(BaseField):
    default = []
    types = (list,)

    @type_validator
    def validate_value(self, value):
        if not all(map(lambda x: isinstance(x, int), value)):
            raise ValidationError(f'{repr(self.name)} field must contains only int types')
