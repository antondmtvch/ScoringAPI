import unittest
import logging
import subprocess

from unittest.mock import Mock, patch
from time import sleep
from redis.exceptions import ConnectionError, TimeoutError

from scoring_api.api.exceptions import StoreConnectionError
from scoring_api.api.store import RedisStore
from scoring_api.tests.helpers import cases

logger = logging.getLogger(__name__)


class IntegrationTestCase(unittest.TestCase):
    rds_test_db = 1
    rds_port = 6379
    rds_proc = None

    @classmethod
    def setUpClass(cls):
        logger.info(f'Starting redis server on {cls.rds_port}')
        cls.rds_proc = subprocess.Popen(['redis-server', '--port', str(cls.rds_port)])
        cls.storage = RedisStore(port=cls.rds_port, db=cls.rds_test_db)

    @classmethod
    def tearDownClass(cls):
        logger.info(f'Terminating redis server')
        cls.rds_proc.terminate()
        cls.rds_proc.wait()

    def setUp(self):
        self.storage.set_connection()
        self.storage.conn.flushdb()

    def add_interests(self, key, interests):
        self.storage.conn.sadd(key, *interests)

    def break_connection(self):
        self.storage.conn = Mock(
            set=Mock(side_effect=ConnectionError),
            get=Mock(side_effect=TimeoutError),
            smembers=Mock(side_effect=TimeoutError),
        )

    @cases(
        [
            ['foo', 1000], ['bar', 5000], ['baz', 3000]
        ]
    )
    def test_storage_cache(self, arguments):
        key, val = arguments
        self.storage.cache_set(key, val, expire_ms=10)
        response = int(self.storage.cache_get(key))
        self.assertEqual(response, val)

    @cases(
        [
            'foo', 'bar', 'baz',
        ]
    )
    def test_storage_cache_expire(self, arguments):
        self.assertIsNone(self.storage.cache_get(arguments))

    @cases(
        [
            ['foo', [b'sport', b'pets']],
            ['bar', [b'music', b'geek']],
            ['baz', [b'books', b'cars']]
        ]
    )
    def test_storage_get(self, arguments):
        key, interests = arguments
        self.add_interests(key, interests)
        self.assertListEqual(sorted(list(self.storage.get(key))), sorted(interests))

    @cases(
        [
            ['foo', 1000], ['bar', 5000], ['baz', 3000]
        ]
    )
    @patch('scoring_api.api.store.RETRY_DELAY', 0)
    @patch('scoring_api.api.store.RETRY_COUNT', 1)
    def test_connection_error_storage_cache(self, arguments):
        key, val = arguments
        self.break_connection()
        self.assertIsNone(self.storage.cache_set(key, val, 10))
        self.assertIsNone(self.storage.cache_get(key))

    @cases(
        [
            'foo', 'bar', 'baz'
        ]
    )
    @patch('scoring_api.api.store.RETRY_DELAY', 0)
    @patch('scoring_api.api.store.RETRY_COUNT', 1)
    def test_connection_error_storage_get(self, arguments):
        self.break_connection()
        with self.assertRaises(StoreConnectionError):
            self.storage.get(arguments)


if __name__ == '__main__':
    unittest.main()
