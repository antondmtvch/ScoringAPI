import redis
from redis.exceptions import TimeoutError, ConnectionError


def retry(n):
    def deco(method):
        def wrapper(*args, **kwargs):
            error = None
            for _ in range(n):
                try:
                    return method(*args, **kwargs)
                except (ConnectionError, TimeoutError) as err:
                    error = err
            else:
                raise StoreConnectionError(error)
        return wrapper
    return deco


class StoreConnectionError(Exception):
    pass


class StoreMetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(StoreMetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisStore(metaclass=StoreMetaSingleton):
    def __init__(self, **connection_args):
        """
        Default connection args:
            host='localhost'
            port=6379
            db=0
            password=None
            socket_timeout=None
            socket_connect_timeout=None
            socket_keepalive=None
            socket_keepalive_options=None
            unix_socket_path=None
            encoding='utf-8'
            encoding_errors='strict'
            charset=None
            errors=None
            decode_responses=False
            retry_on_timeout=False
            ssl=False
            ssl_keyfile=None
            ssl_certfile=None
            ssl_cert_reqs='required'
            ssl_ca_certs=None
            ssl_check_hostname=False
            max_connections=None
            single_connection_client=False
            health_check_interval=0
            client_name=None
            username=None
        """
        self.connection_args = connection_args
        self._conn = None

    @property
    def conn(self):
        if not self._conn:
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.Redis(connection_pool=redis.ConnectionPool(**self.connection_args))

    @retry(3)
    def set(self, key, value):
        return self.conn.set(key, value)

    @retry(3)
    def get(self, key):
        return self.conn.get(key)

    @retry(3)
    def cache_get(self, key):
        return self.conn.get(key)

    @retry(3)
    def cache_set(self, key, value, expire):
        return self.conn.set(key, value, ex=expire)
