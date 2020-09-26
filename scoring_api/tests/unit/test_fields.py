import unittest
from datetime import datetime, timedelta

from scoring_api.api.fields import CharField, EmailField, ArgumentsField, PhoneField, DateField, GenderField, \
    BirthDayField, ClientIDsField
from scoring_api.tests.helpers import cases
from scoring_api.api.exceptions import ValidationError


class CharFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = CharField(False, False)
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, ''],
            [False, False, None],
            [False, True, 11111],
            [True, True, []],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, 'test'],
            [True, True, 'test'],
            [True, True, ''],
            [False, True, ''],
            [False, True, None],
        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class EmailFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = EmailField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, ''],
            [False, False, None],
            [False, True, 1],
            [True, False, {}],
            [True, False, 'test.email'],
            [True, False, 'test@email'],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, 'test@email.test'],
            [True, True, 'test@email.test'],
            [False, True, 'test@email.test'],
            [False, True, ''],
            [True, True, None],
        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class ArgumentsFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = ArgumentsField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [False, False, None],
            [False, True, 1],
            [True, False, []],
            [True, False, {}],
            [False, False, {}],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, {'key': 1}],
            [False, False, {'key': 'val'}],
            [True, True, {}],
            [False, True, {}],
            [False, True, None],

        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class PhoneFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = PhoneField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [False, False, '89991115555'],
            [False, False, '899911155551'],
            [False, False, 89991115555],
            [False, False, '+79991115555'],
            [False, False, '+7(999)111-55-55'],
            [False, False, 1],
            [True, False, []],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, '79991115555'],
            [True, False, 79991115555],
            [True, True, None],
            [False, True, ''],

        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class DateFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = DateField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [False, False, '01-01-2000'],
            [False, False, '1-1-2000'],
            [False, False, '2000.01.01'],
            [False, False, 123],
            [False, True, []],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, '01.01.2000'],
            [True, False, '1.1.2000'],
            [True, True, ''],
            [False, True, None],

        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class GenderFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = GenderField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [False, False, -1],
            [False, False, 3],
            [False, False, 2.1],
            [False, True, []],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, True, 0],
            [True, False, 1],
            [False, True, 2],
            [False, True, None],
            [False, True, ''],

        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class BirthDayFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = BirthDayField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [False, False, '01-01-2000'],
            [False, False, '1-1-2000'],
            [False, False, (datetime.now() - timedelta(365 * 70)).strftime('%d.%m.%Y')],
            [False, False, (datetime.now() + timedelta(1)).strftime('%d.%m.%Y')],
            [False, False, 123],
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, '01.01.2000'],
            [True, False, '1.1.2000'],
            [True, False, (datetime.now() - timedelta(365 * 69)).strftime('%d.%m.%Y')],
            [True, False, datetime.now().strftime('%d.%m.%Y')],
            [True, True, None],
            [True, True, ''],

        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


class ClientIDsFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = ClientIDsField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, attrs):
        required, nullable = attrs
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            [True, False, None],
            [True, False, ''],
            [False, False, 'test'],
            [True, False, []],
            [False, False, ['1', '2']],
            [False, False, [0.1, 0.1]],
            [False, False, {}],
            [False, False, 123],
            [False, False, []]
        ]
    )
    def test_set_invalid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        with self.assertRaises(ValidationError):
            self.field.validate(value)

    @cases(
        [
            [True, False, [1, 2]],
            [True, True, []],
            [False, True, []],
            [False, True, [1]],
            [False, False, [1, 2]],
            [False, True, None],
        ]
    )
    def test_set_valid_value(self, case):
        *attrs, value = case
        self.init_field(attrs)
        self.assertIsNone(self.field.validate(value))


if __name__ == '__main__':
    unittest.main()
