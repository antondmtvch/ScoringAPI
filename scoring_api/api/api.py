import json
import logging
import hashlib
import uuid

from datetime import datetime
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from scoring_api.api.scoring import get_interests, get_score
from scoring_api.api.exceptions import ValidationError
from scoring_api.api.store import RedisStore
from scoring_api.api.fields import BaseField, CharField, DateField, ClientIDsField, EmailField, PhoneField, \
    BirthDayField, GenderField, ArgumentsField, GENDERS

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


class RequestMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = []
        for k, v in attrs.items():
            if isinstance(v, BaseField):
                fields.append(k)
        attrs['fields'] = fields
        cls = super(RequestMeta, mcs).__new__(mcs, name, bases, attrs)
        return cls


class Request(metaclass=RequestMeta):
    def __init__(self, **kwargs):
        for name in self.fields:
            setattr(self, name, kwargs.get(name))
        self.context = {}

    def validate_fields(self):
        for name in self.fields:
            obj = self.__class__.__dict__[name]
            obj.validate(getattr(self, name))


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context.update({'nclients': len(self.client_ids) if self.client_ids else 0})


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context.update({'has': [name for name in self.fields if getattr(self, name) not in {None, ''}]})

    def validate_fields(self):
        super().validate_fields()
        if not any(
                [
                    bool((self.gender in GENDERS.keys() and self.birthday)),
                    bool((self.phone and self.email)),
                    bool((self.first_name and self.last_name))
                ]):
            raise ValidationError(f'at least one pair must be present: phone-email or name-surname or gender-birthday '
                                  f'with non-empty values.')


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(request, ctx, store):
    score = 42
    if check_auth(request):
        score_request = OnlineScoreRequest(**request.arguments)
        score_request.validate_fields()
        ctx.update(score_request.context)
        if not request.is_admin:
            score = get_score(store=store, phone=score_request.phone, email=score_request.email,
                              birthday=score_request.birthday, gender=score_request.gender,
                              first_name=score_request.first_name, last_name=score_request.last_name)
            return {'score': score}, OK
        return {'score': score}, OK
    return None, FORBIDDEN


def clients_interests_handler(request, ctx, store):
    if check_auth(request):
        interests_request = ClientsInterestsRequest(**request.arguments)
        interests_request.validate_fields()
        ctx.update(interests_request.context)
        return {str(i): get_interests(store, i) for i in interests_request.client_ids}, OK
    return None, FORBIDDEN


def method_handler(request, ctx, store):
    response, code = None, INVALID_REQUEST
    handlers = {
        'online_score': online_score_handler,
        'clients_interests': clients_interests_handler
    }
    if body := request.get('body'):
        try:
            request = MethodRequest(**body)
            request.validate_fields()
            if handler := handlers.get(request.method):
                response, code = handler(store=store, ctx=ctx, request=request)
            return response, code
        except ValidationError as err:
            logging.exception(err)
            return str(err), code
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = RedisStore()

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
        self.wfile.write(json.dumps(r).encode('utf-8'))
        return


def main():
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--host", action="store", type=str, default="localhost")
    opts, args = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer((opts.host, opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
