import unittest
from scoring_api.api.store import RedisStore
from unittest.mock import Mock, patch
from redis.exceptions import TimeoutError, ConnectionError
from scoring_api.api.exceptions import StoreConnectionError


class StoreTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage = RedisStore()
        cls.storage.conn = Mock(
            smembers=Mock(side_effect=ConnectionError),
            get=Mock(side_effect=ConnectionError),
            set=Mock(side_effect=ConnectionError),
        )

    def test_singleton_object(self):
        self.assertIs(self.storage, RedisStore())

    @patch('scoring_api.api.store.RETRY_DELAY', 0)
    @patch('scoring_api.api.store.RETRY_COUNT', 1)
    def test_storage_connection_error(self):
        with self.assertRaises(StoreConnectionError):
            self.storage.get('key')

    @patch('scoring_api.api.store.RETRY_DELAY', 0)
    @patch('scoring_api.api.store.RETRY_COUNT', 1)
    def test_cache_connection_error(self):
        self.assertIsNone(self.storage.cache_get('key'))
        self.assertIsNone(self.storage.cache_set('key', 'value', expire=0))


if __name__ == '__main__':
    unittest.main()
