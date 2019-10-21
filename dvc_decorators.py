from functools import wraps
from flask_jwt_extended import get_jwt_claims
from flask import jsonify
import status


def test_decorator(orig_func):
    @wraps(orig_func)
    def decorated_function(*args, **kwargs):
        x = get_jwt_claims()
        print(x)
        return orig_func(*args, **kwargs)
    return decorated_function


def jwt_access_level(access_level):
    def actual_decorator(orig_func):
        @wraps(orig_func)
        def decorated_function(*args, **kwargs):
            jwt_encoded_access_level = get_jwt_claims()['access_level']
            if jwt_encoded_access_level < access_level:
                resp = jsonify({"error": "Insufficient access level for user"})
                resp.status_code = status.HTTP_401_UNAUTHORIZED
                return resp
            else:
                return orig_func(*args, **kwargs)
        return decorated_function
    return actual_decorator
