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

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': None},
            {'required': False, 'nullable': True, 'value': 11111},
            {'required': True, 'nullable': True, 'value': []},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': 'test'},
            {'required': True, 'nullable': False, 'value': 'test'},
            {'required': True, 'nullable': True, 'value': 'test'},
            {'required': False, 'nullable': True, 'value': ''},
            {'required': False, 'nullable': True, 'value': None},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class EmailFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = EmailField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': None},
            {'required': False, 'nullable': True, 'value': 1},
            {'required': True, 'nullable': False, 'value': {}},
            {'required': True, 'nullable': False, 'value': 'test.email'},
            {'required': True, 'nullable': False, 'value': 'test@email'},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': 'test@email.test'},
            {'required': True, 'nullable': True, 'value': 'test@email.test'},
            {'required': False, 'nullable': True, 'value': 'test@email.test'},
            {'required': False, 'nullable': True, 'value': ''},
            {'required': True, 'nullable': True, 'value': None},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class ArgumentsFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = ArgumentsField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': False, 'nullable': False, 'value': None},
            {'required': False, 'nullable': True, 'value': 1},
            {'required': True, 'nullable': False, 'value': []},
            {'required': True, 'nullable': False, 'value': {}},
            {'required': False, 'nullable': False, 'value': {}},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': {'key': 1}},
            {'required': False, 'nullable': False, 'value': {'key': 'val'}},
            {'required': True, 'nullable': True, 'value': {}},
            {'required': False, 'nullable': True, 'value': {}},
            {'required': False, 'nullable': True, 'value': None},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class PhoneFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = PhoneField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': False, 'nullable': False, 'value': '89991115555'},
            {'required': False, 'nullable': False, 'value': '899911155551'},
            {'required': False, 'nullable': False, 'value': 89991115555},
            {'required': False, 'nullable': False, 'value': '+79991115555'},
            {'required': False, 'nullable': False, 'value': '+7(999)111-55-55'},
            {'required': False, 'nullable': False, 'value': 1},
            {'required': True, 'nullable': False, 'value': []},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': '79991115555'},
            {'required': True, 'nullable': False, 'value': 79991115555},
            {'required': True, 'nullable': True, 'value': None},
            {'required': False, 'nullable': True, 'value': ''},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class DateFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = DateField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': False, 'nullable': False, 'value': '01-01-2000'},
            {'required': False, 'nullable': False, 'value': '1-1-2000'},
            {'required': False, 'nullable': False, 'value': '2000.01.01'},
            {'required': False, 'nullable': False, 'value': 123},
            {'required': False, 'nullable': True, 'value': []},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': '01.01.2000'},
            {'required': True, 'nullable': False, 'value': '1.1.2000'},
            {'required': True, 'nullable': True, 'value': ''},
            {'required': False, 'nullable': True, 'value': None},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class GenderFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = GenderField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': False, 'nullable': False, 'value': -1},
            {'required': False, 'nullable': False, 'value': 3},
            {'required': False, 'nullable': False, 'value': 2.1},
            {'required': False, 'nullable': True, 'value': []},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': True, 'value': 0},
            {'required': True, 'nullable': False, 'value': 1},
            {'required': False, 'nullable': True, 'value': 2},
            {'required': False, 'nullable': True, 'value': None},
            {'required': False, 'nullable': True, 'value': ''},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class BirthDayFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = BirthDayField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': False, 'nullable': False, 'value': '01-01-2000'},
            {'required': False, 'nullable': False, 'value': '1-1-2000'},
            {'required': False, 'nullable': False, 'value': (datetime.now() - timedelta(365 * 70)).strftime('%d.%m.%Y')},
            {'required': False, 'nullable': False, 'value': (datetime.now() + timedelta(1)).strftime('%d.%m.%Y')},
            {'required': False, 'nullable': False, 'value': 123},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': '01.01.2000'},
            {'required': True, 'nullable': False, 'value': '1.1.2000'},
            {'required': True, 'nullable': False, 'value': (datetime.now() - timedelta(365 * 69)).strftime('%d.%m.%Y')},
            {'required': True, 'nullable': False, 'value': datetime.now().strftime('%d.%m.%Y')},
            {'required': True, 'nullable': True, 'value': None},
            {'required': True, 'nullable': True, 'value': ''},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


class ClientIDsFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = ClientIDsField()
        self.field.__set_name__(self.field, self.field.__class__.__name__)

    def init_field(self, required, nullable):
        self.field.required = required
        self.field.nullable = nullable

    @cases(
        [
            {'required': True, 'nullable': False, 'value': None},
            {'required': True, 'nullable': False, 'value': ''},
            {'required': False, 'nullable': False, 'value': 'test'},
            {'required': True, 'nullable': False, 'value': []},
            {'required': False, 'nullable': False, 'value': ['1', '2']},
            {'required': False, 'nullable': False, 'value': [0.1, 0.1]},
            {'required': False, 'nullable': False, 'value': {}},
            {'required': False, 'nullable': False, 'value': 123},
            {'required': False, 'nullable': False, 'value': []},
        ]
    )
    def test_set_invalid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        with self.assertRaises(ValidationError):
            self.field.validate(case['value'])

    @cases(
        [
            {'required': True, 'nullable': False, 'value': [1, 2]},
            {'required': True, 'nullable': True, 'value': []},
            {'required': False, 'nullable': True, 'value': []},
            {'required': False, 'nullable': True, 'value': [1]},
            {'required': False, 'nullable': False, 'value': [1, 2]},
            {'required': False, 'nullable': True, 'value': None},
        ]
    )
    def test_set_valid_value(self, case):
        self.init_field(case['required'], case['nullable'])
        self.assertIsNone(self.field.validate(case['value']))


if __name__ == '__main__':
    unittest.main()
