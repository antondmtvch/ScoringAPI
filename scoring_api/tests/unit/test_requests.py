import unittest

from scoring_api.api.api import ClientsInterestsRequest, OnlineScoreRequest, MethodRequest
from scoring_api.api.exceptions import ValidationError
from scoring_api.tests.helpers import cases


class ClientsInterestsRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.request = ClientsInterestsRequest

    def test_fields_attribute_value(self):
        self.assertListEqual(self.request().fields, ['client_ids', 'date'])

    @cases(
        [
            {'client_ids': [1, 2], 'date': '01.01.2000'},
            {'client_ids': [1], 'date': '1.1.2000'},
            {'client_ids': [1, 2], 'date': ''},
            {'client_ids': [1, 2], 'date': None},
        ]
    )
    def test_valid_values(self, case):
        request = self.request(**case)
        self.assertIsNone(request.validate_fields())

    @cases(
        [
            {'client_ids': ['1', '2'], 'date': '01.01.2000'},
            {'client_ids': ['1', 2], 'date': '1.1.2000'},
            {'client_ids': [], 'date': '1.1.2000'},
            {'client_ids': None, 'date': '1.1.2000'},
            {'client_ids': '', 'date': '1.1.2000'},
            {'client_ids': [1, 2], 'date': '01-01-2000'},
        ]
    )
    def test_invalid_values(self, case):
        request = self.request(**case)
        with self.assertRaises(ValidationError):
            request.validate_fields()

    @cases(
        [
            [{'client_ids': [], 'date': None}, 0],
            [{'client_ids': [1], 'date': None}, 1],
            [{'client_ids': None, 'date': None}, 0],
            [{'client_ids': [1, 2, 3], 'date': None}, 3],
            [{'client_ids': '', 'date': None}, 0],
        ]
    )
    def test_context(self, case):
        request_args, nclients_value = case
        request = self.request(**request_args)
        self.assertDictEqual(request.context, {'nclients': nclients_value})


class OnlineScoreRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.request = OnlineScoreRequest

    def test_fields_attribute_value(self):
        self.assertListEqual(self.request().fields, ['first_name', 'last_name', 'email', 'phone', 'birthday', 'gender'])

    @cases(
        [
            {
                'first_name': 'test', 'last_name': 'test',
                'email': '', 'phone': '',
                'birthday': '', 'gender': ''
            },
            {
                'first_name': '', 'last_name': '',
                'email': 'test@test.test', 'phone': '79991112233',
                'birthday': '', 'gender': ''
            },
            {
                'first_name': '', 'last_name': '',
                'email': 'test@test.test', 'phone': 79991112233,
                'birthday': '', 'gender': ''
            },
            {
                'first_name': '', 'last_name': '',
                'email': '', 'phone': '',
                'birthday': '01.01.2000', 'gender': 1
            },
        ]
    )
    def test_valid_pairs(self, case):
        request = self.request(**case)
        self.assertIsNone(request.validate_fields())

    @cases(
        [
            {
                'first_name': 'test', 'last_name': None,
                'email': None, 'phone': 79991112233,
                'birthday': None, 'gender': 1
            },
            {
                'first_name': 'test', 'last_name': None,
                'email': 'test@test.test', 'phone': None,
                'birthday': None, 'gender': 1
            },
            {
                'first_name': 'test', 'last_name': None,
                'email': 'test@test.test', 'phone': None,
                'birthday': '01.01.2000', 'gender': None
            },
            {
                'first_name': None, 'last_name': None,
                'email': 'test@test', 'phone': '79991112233',
                'birthday': None, 'gender': None
            },
            {
                'first_name': None, 'last_name': None,
                'email': None, 'phone': None,
                'birthday': '01.01.2000', 'gender': 4
            },
        ]
    )
    def test_invalid_pairs(self, case):
        request = self.request(**case)
        with self.assertRaises(ValidationError):
            request.validate_fields()

    @cases(
        [
            {
                'first_name': None, 'last_name': None,
                'email': None, 'phone': None,
                'birthday': None, 'gender': None
            },
            {
                'first_name': '', 'last_name': '',
                'email': '', 'phone': '',
                'birthday': '', 'gender': ''
            },
            {
                'first_name': 'name', 'last_name': 'name',
                'email': None, 'phone': 79991112233,
                'birthday': None, 'gender': 1
            },
        ]
    )
    def test_context(self, case):
        request = self.request(**case)
        self.assertDictEqual(request.context, {'has': [k for k in case if case[k]]})


class MethodRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.request = MethodRequest

    def test_fields_attribute_value(self):
        self.assertListEqual(self.request().fields, ['account', 'login', 'token', 'arguments', 'method'])

    @cases(
        [
            {'account': '', 'login': '', 'token': '', 'arguments': {}, 'method': 'test_method'},
            {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 'test_method'},
            {'account': None, 'login': None, 'token': None, 'arguments': {'arg': None}, 'method': 'test_method'},
        ]
    )
    def test_valid_values(self, case):
        request = self.request(**case)
        self.assertIsNone(request.validate_fields())

    @cases(
        [
            {'account': '', 'login': '', 'token': '', 'arguments': {}, 'method': None},
            {'account': '', 'login': '', 'token': '', 'arguments': {}, 'method': ''},
            {'account': '', 'login': '', 'token': '', 'arguments': {}, 'method': 1},
            {'account': '', 'login': '', 'token': '', 'arguments': [], 'method': 'test_method'},
            {'account': 1, 'login': None, 'token': None, 'arguments': None, 'method': 'test_method'},
            {'account': None, 'login': 1, 'token': None, 'arguments': None, 'method': 'test_method'},
            {'account': None, 'login': None, 'token': 1, 'arguments': None, 'method': 'test_method'},
            {'account': None, 'login': None, 'token': None, 'arguments': None, 'method': 1},
        ]
    )
    def test_invalid_values(self, case):
        request = self.request(**case)
        with self.assertRaises(ValidationError):
            request.validate_fields()

    @cases(
        [
            {'account': None, 'login': '', 'token': None, 'arguments': {}, 'method': 'test_method'},
            {'account': None, 'login': None, 'token': None, 'arguments': {}, 'method': 'test_method'},
            {'account': None, 'login': 'user', 'token': None, 'arguments': {}, 'method': 'test_method'},
        ]
    )
    def test_invalid_admin_login(self, case):
        request = self.request(**case)
        self.assertFalse(request.is_admin)

    @cases(
        [{'account': None, 'login': 'admin', 'token': None, 'arguments': {}, 'method': 'test_method'},]
    )
    def test_valid_admin_login(self, case):
        request = self.request(**case)
        self.assertTrue(request.is_admin)


if __name__ == '__main__':
    unittest.main()