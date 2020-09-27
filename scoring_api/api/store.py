import redis
from time import sleep
from scoring_api.api.exceptions import StoreConnectionError
from redis.exceptions import TimeoutError, ConnectionError

RETRY_COUNT = 3
RETRY_DELAY = 0.5


def retry_connect(raise_on_failure=True):
    def decorator(method):
        def wrapper(*args, **kwargs):
            error = None
            for _ in range(RETRY_COUNT):
                try:
                    return method(*args, **kwargs)
                except (ConnectionError, TimeoutError) as err:
                    error = err
                    sleep(RETRY_DELAY)
            else:
                if raise_on_failure:
                    raise StoreConnectionError(error)
                else:
                    return None
        return wrapper
    return decorator


class StoreMetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(StoreMetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisStore(metaclass=StoreMetaSingleton):
    _conn = None

    def __init__(self, **connection_kwargs):
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
        self.connection_kwargs = connection_kwargs

    def set_connection(self):
        try:
            conn = redis.Redis(connection_pool=redis.ConnectionPool(**self.connection_kwargs))
            conn.ping()
        except ConnectionError as err:
            raise StoreConnectionError(err)
        self._conn = conn

    @retry_connect(raise_on_failure=True)
    def set(self, key, value):
        return self._conn.set(key, value)

    @retry_connect(raise_on_failure=True)
    def get(self, key):
        return self._conn.get(key)

    @retry_connect(raise_on_failure=False)
    def cache_get(self, key):
        return self._conn.get(key)

    @retry_connect(raise_on_failure=False)
    def cache_set(self, key, value, expire):
        return self._conn.set(key, value, ex=expire)
