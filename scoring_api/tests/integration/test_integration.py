import hashlib
import random
import socket
import unittest
import logging
import subprocess
import threading
import requests

from datetime import datetime
from http.server import HTTPServer
from scoring_api.api import api
from scoring_api.api.api import MainHTTPHandler
from scoring_api.api.store import RedisStore
from scoring_api.api.scoring import get_interests
from scoring_api.tests.helpers import cases

logger = logging.getLogger(__name__)


def find_free_port():
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(('0.0.0.0', 0))
    free_socket.listen(1)
    port = free_socket.getsockname()[1]
    free_socket.close()
    return port


class IntegrationTestCase(unittest.TestCase):
    api_proc = None
    rds_proc = None

    @classmethod
    def setUpClass(cls):
        logger.info(f'Starting redis server')

        cls.rds_proc = subprocess.Popen(['redis-server', '--port', '6379'])
        cls.redis = RedisStore(port=6379, db=1)
        cls.redis.set_connection()

        cls.port = find_free_port()
        logger.info(f'Starting http server on {cls.port}')

        server = HTTPServer(("localhost", cls.port), MainHTTPHandler)
        cls.api_proc = threading.Thread(target=server.serve_forever)
        cls.api_proc.daemon = True
        cls.api_proc.start()

    @classmethod
    def tearDownClass(cls):
        logger.info(f'Terminating redis server')
        cls.rds_proc.terminate()
        cls.rds_proc.wait()

    def setUp(self):
        self.redis.conn.flushall()

    def add_interests_to_redis(self, cid_list):
        for cid in cid_list:
            interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek"]
            key = ('i:%s' % cid).encode('utf-8')
            val = [i.encode('utf-8') for i in random.sample(interests, 2)]
            self.redis.conn.sadd(key, *val)

    @staticmethod
    def create_score_key(**kwargs):
        birthday = kwargs.get('birthday')
        phone = kwargs.get('phone')

        key_parts = [
            kwargs.get('first_name', ''),
            kwargs.get('last_name', ''),
            str(phone) if phone else '',
            datetime.strptime(birthday, '%d.%m.%Y').strftime('%Y%m%d') if birthday else '',
        ]
        return 'uid:' + hashlib.md5(''.join(key_parts).encode('utf-8')).hexdigest()

    def get_response(self, request):
        return requests.post(f'http://127.0.0.1:{self.port}/method/', json=request)

    @staticmethod
    def set_valid_auth(request):
        if request.get('login') == api.ADMIN_LOGIN:
            request['token'] = hashlib.sha512(
                (datetime.now().strftime('%Y%m%d%H') + api.ADMIN_SALT).encode('utf-8')).hexdigest()
        else:
            msg = request.get('account', '') + request.get('login', '') + api.SALT
            request['token'] = hashlib.sha512(msg.encode('utf-8')).hexdigest()

    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ])
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response = self.get_response(request)
        self.assertEqual(api.OK, response.status_code)
        data = response.json()
        score = data['response']['score']
        self.assertTrue(score >= 0)
        key = self.create_score_key(**arguments)
        self.assertEqual(float(self.redis.cache_get(key)), score)

    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_ok_interests_request_empty_storage(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response = self.get_response(request)
        self.assertEqual(response.status_code, api.OK)
        data = response.json()
        for k in data['response']:
            self.assertListEqual(data['response'][k], [])

    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_ok_interests_request_nonempty_storage(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.add_interests_to_redis(arguments['client_ids'])
        self.set_valid_auth(request)
        response = self.get_response(request)
        self.assertEqual(response.status_code, api.OK)
        data = response.json()
        for k in data['response']:
            self.assertListEqual(data['response'][k], get_interests(self.redis, k))


if __name__ == '__main__':
    unittest.main()
