import abc
import json
import datetime
import logging
import hashlib
import uuid

from optparse import OptionParser
from weakref import WeakKeyDictionary
from http.server import HTTPServer, BaseHTTPRequestHandler
from scoring_api.api.scoring import get_interests, get_score
from scoring_api.api.validators import (
    type_validator, email_validator, phone_validator, date_validator, birthday_validator
)

SALT, ADMIN_LOGIN, ADMIN_SALT = 'Otus', 'admin', '42'

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
UNKNOWN, MALE, FEMALE = 0, 1, 2

GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class BaseField(abc.ABC):
    def __init__(self, required=False, nullable=False):
        self.default = None
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        self.prevalidate(value)
        if value is not self.default:
            self.validate(value)
        self.data[instance] = value

    def prevalidate(self, value):
        if (value is self.default) and (not self.nullable or self.required):
            raise ValueError(f'{self.__class__.__name__} is required')
        elif not value and not self.nullable:
            raise ValueError(f'{self.__class__.__name__} not be nullable')

    @abc.abstractmethod
    def validate(self, value): pass


class CharField(BaseField):
    @type_validator(str, None)
    def validate(self, value): pass


class EmailField(CharField):
    @email_validator
    def validate(self, value): pass


class ArgumentsField(BaseField):
    @type_validator(dict)
    def validate(self, value): pass


class PhoneField(BaseField):
    @phone_validator
    def validate(self, value): pass


class DateField(CharField):
    @date_validator(fmt='%d.%m.%Y')
    def validate(self, value): pass


class BirthDayField(DateField):
    @birthday_validator(max_years=70, fmt='%d.%m.%Y')
    def validate(self, value): pass


class GenderField(BaseField):
    @type_validator(int)
    def validate(self, value):
        if value not in GENDERS.keys():
            raise ValueError(f'{self.__class__.__name__} value must be 0 or 1 or 2, not {value}')


class ClientIDsField(BaseField):
    @type_validator(list)
    def validate(self, value):
        if not all(map(lambda x: isinstance(x, int), value)):
            raise TypeError(f'{self.__class__.__name__}: {value} must contains only int types')


class BaseRequest(abc.ABC):
    _context = None

    @property
    @abc.abstractmethod
    def context(self): pass


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def __init__(self, client_ids=None, date=None):
        self.client_ids = [] if not client_ids else client_ids
        self.date = date
        self.context = {'nclients': len(self.client_ids)}

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, first_name=None, last_name=None, email=None, phone=None, birthday=None, gender=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender
        self.context = {'has': [v for v in self.get_attribute_values() if v]}
        self.validate()

    def get_attribute_values(self):
        attrs = ((k, v) for k, v in self.__class__.__dict__.items() if isinstance(v, BaseField))
        return [n for n, _ in attrs if self.__getattribute__(n) not in {None, ''}]

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    def validate(self):
        if (self.gender in GENDERS.keys() and self.birthday) or (self.phone and self.email) \
                or (self.first_name and self.last_name): pass
        else:
            raise ValueError(f'{self.__class__.__name__}: at least one pair must be present phone-email, '
                             f'name-surname, gender-birthday with non-empty values.')


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, account=None, login=None, token=None, arguments=None, method=None):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = {} if not arguments else arguments
        self.method = method

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(request, ctx, store):
    score = 42
    if check_auth(request):
        score_request = OnlineScoreRequest(**request.arguments)
        ctx.update(score_request.context)
        if not request.is_admin:
            score = get_score(store=store, phone=score_request.phone, email=score_request.email,
                              birthday=score_request.birthday, gender=score_request.gender,
                              first_name=score_request.first_name, last_name=score_request.last_name)
            return {'score': score}, OK
        return {'score': score}, OK
    return ERRORS[FORBIDDEN], FORBIDDEN


def clients_interests_handler(request, ctx, store):
    if check_auth(request):
        interests_request = ClientsInterestsRequest(**request.arguments)
        ctx.update(interests_request.context)
        return {str(i): get_interests(store, i) for i in interests_request.client_ids}, OK
    return ERRORS[FORBIDDEN], FORBIDDEN


def method_handler(request, ctx, store):
    response, code = ERRORS[INVALID_REQUEST], INVALID_REQUEST
    handlers = {
        'online_score': online_score_handler,
        'clients_interests': clients_interests_handler
    }
    if body := request.get('body'):
        try:
            request = MethodRequest(**body)
            if handler := handlers.get(request.method):
                response, code = handler(store=store, ctx=ctx, request=request)
            return response, code
        except (TypeError, ValueError) as e:
            return response, code
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    @staticmethod
    def get_request_id(headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request, data_string = None, None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception as e:
            logging.exception(e)
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
        self.wfile.write(json.dumps(r).encode('utf-8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    opts, args = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
