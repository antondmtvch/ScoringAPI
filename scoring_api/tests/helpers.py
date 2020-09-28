import logging
import functools

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
logger = logging.getLogger(__name__)


def cases(_cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in _cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception as err:
                    logger.error(new_args, exc_info=True)
                    raise err
        return wrapper
    return decorator
