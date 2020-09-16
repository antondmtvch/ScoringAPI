import re
import abc
import json
import datetime
import logging
import hashlib
import uuid

from datetime import datetime, timedelta
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

PHONE_PATTERN = re.compile(r'^7\d{10}$')
EMAIL_PATTERN = re.compile(r'^\w+@\w+\.\w+$')


class Field(abc.ABC):
    def __init__(self, required=False, nullable=False):
        self._required = required
        self._nullable = nullable
        self._value = None

    def __eq__(self, other):
        return self._value == other

    @property
    def value(self):
        return self._value

    @property
    def required(self):
        return self._required

    @property
    def nullable(self):
        return self._nullable

    @value.setter
    def value(self, value):
        self._validate(value)
        self._value = value

    @abc.abstractmethod
    def _validate(self, value):
        pass


class CharField(Field):
    def _validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f'{self.__class__.__name__} value must be str, not {value.__class__.__name__}')


class EmailField(CharField):
    def _validate(self, value):
        super()._validate(value)
        if not re.match(EMAIL_PATTERN, value):
            raise ValueError(f'{value} is not valid email')


class ArgumentsField(Field):
    def _validate(self, value):
        if not isinstance(value, dict):
            raise TypeError(f'{self.__class__.__name__} must be dict, not {value.__class__.__name__}')


class PhoneField(Field):
    def _validate(self, value):
        if not isinstance(value, (str, int)):
            raise TypeError(f'{self.__class__.__name__} must be str or int, not {value.__class__.__name__}')
        elif not re.match(PHONE_PATTERN, str(value)):
            raise ValueError(f'{value} is not valid phone number')


class DateField(Field):
    def _validate(self, value):
        super()._validate(value)
        try:
            self.dt = datetime.strptime(value, '%d.%m.%Y')
        except ValueError as err:
            raise ValueError(err)


class BirthDayField(DateField):
    def _validate(self, value):
        super()._validate(value)
        if self.dt + timedelta(days=365 * 70) < datetime.now():
            raise ValueError(f'more than 70 years have passed since {repr(value)}')


class GenderField(Field):
    def _validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f'{self.__class__.__name__} must be int, not {value.__class__.__name__}')
        elif value not in GENDERS.keys():
            raise ValueError(f'{self.__class__.__name__} value must be 0 or 1 or 2, not {value}')


class ClientIDsField(Field):
    def _validate(self, value):
        if not isinstance(value, list):
            raise TypeError(f'{self.__class__.__name__} must be list, not {value.__class__.__name__}')
        elif not all(map(lambda x: isinstance(x, int), value)):
            raise TypeError(f'{self.__class__.__name__} must contains only int types')


class Request(abc.ABC):
    def __init__(self, **kwargs):
        for attr in kwargs:
            if hasattr(self, attr):
                setattr(self, attr, kwargs[attr])

    @abc.abstractmethod
    def _validate(self):
        pass


class ClientsInterestsRequest(Request):
    _client_ids = ClientIDsField(required=True)
    _date = DateField(required=False, nullable=True)

    @property
    def client_ids(self):
        return self._client_ids.value

    @client_ids.setter
    def client_ids(self, value):
        self._client_ids.value = value

    @property
    def date(self):
        return self._date.value

    @date.setter
    def date(self, value):
        self._date.value = value

    def _validate(self):
        pass


class OnlineScoreRequest(Request):
    _first_name = CharField(required=False, nullable=True)
    _last_name = CharField(required=False, nullable=True)
    _email = EmailField(required=False, nullable=True)
    _phone = PhoneField(required=False, nullable=True)
    _birthday = BirthDayField(required=False, nullable=True)
    _gender = GenderField(required=False, nullable=True)

    @property
    def first_name(self):
        return self._first_name.value

    @first_name.setter
    def first_name(self, value):
        self._first_name.value = value

    @property
    def last_name(self):
        return self._last_name.value

    @last_name.setter
    def last_name(self, value):
        self._last_name.value = value

    @property
    def email(self):
        return self._email.value

    @email.setter
    def email(self, value):
        self._email.value = value

    @property
    def phone(self):
        return self._phone.value

    @phone.setter
    def phone(self, value):
        self._phone.value = value

    @property
    def birthday(self):
        return self._birthday.value

    @birthday.setter
    def birthday(self, value):
        self._birthday.value = value

    @property
    def gender(self):
        return self._gender.value

    @gender.setter
    def gender(self, value):
        self._gender.value = value

    def _validate(self):
        if (self.phone and self.email) or (self.first_name and self.last_name) or (self.gender and self.birthday):
            pass
        else:
            raise ValueError(f'{self.__class__.__name__}: at least one pair must be present phone-email, '
                             f'name-surname, gender-birthday with non-empty values.')


class MethodRequest(Request):
    _account = CharField(required=False, nullable=True)
    _login = CharField(required=True, nullable=True)
    _token = CharField(required=True, nullable=True)
    _arguments = ArgumentsField(required=True, nullable=True)
    _method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    @property
    def account(self):
        return self._account.value

    @account.setter
    def account(self, value):
        self._account.value = value

    @property
    def login(self):
        return self._login.value

    @login.setter
    def login(self, value):
        self._login.value = value

    @property
    def token(self):
        return self._token.value

    @token.setter
    def token(self, value):
        self._token.value = value

    @property
    def arguments(self):
        return self._arguments.value

    @arguments.setter
    def arguments(self, value):
        self._arguments.value = value

    @property
    def method(self):
        return self._method.value

    @method.setter
    def method(self, value):
        self._method.value = value

    def _validate(self):
        pass


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
