from functools import wraps
import warnings


def ignore_warnings(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as _:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response

    return inner
