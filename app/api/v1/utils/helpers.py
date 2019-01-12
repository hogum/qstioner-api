from functools import wraps
from flask import request

from ...v1.models.users import UserModel

current_user = None
get_raw_auth = None


def verify_pass(value):
    if len(value) < 6:
        raise ValueError("Password should be at least 6 charcters")
    return value


def verify_names(value, item):
    try:
        int(value)
        raise AttributeError(f"{value} is wrong. {item} cannot be a number")

    except ValueError:
        pass


def admin_required(f):
    """
        Protects endpoints accessible to admin user only.
        Ensures only an admin user can access this endpoint.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):

        # We never get here in real sense, consumed by missing Auth header
        # Uncomment when testing manually
        #
        # Verify Logged in
        """if not get_jwt_identity():
            return {
                "Status": 403,
                "Error": "Please log in, okay?"
            }, 403

        user = UserModel.get_by_name(get_jwt_identity())
        if not user:
            return {
                "Status": 400,
                "Error": "Identity unknown"
            }
    """
        if not UserModel.get_by_name(get_jwt_identity()).isAdmin:
            return {
                "Status": 403,
                "Message": "Oops! Only an admin can do that"
            }, 403
        return f(*args, **kwargs)
    return wrapper


def current_user_only(f):
    @wraps(f)
    def wrapper(*args, **kwars):
        url_user_field = request.base_url.split('/')
        user = url_user_field[-2]
        this_user = get_jwt_identity()

        # Comment out if manually testing
        # Handled by missing auth header error
        """
        if not this_user:
            return {
                "Status": 403,
                "Message": "You need to be logged in to do that"
            }, 403
        """

        try:
            uid = int(user)
            user = UserModel.get_by_id(uid)
            if user:
                user = user.username
        except ValueError:
            user = user
        if this_user != user:
            return {
                "Status": 403,
                "Error": "Denied. Not accessible to current user"
            }, 403
        return f(*args, **kwars)
    return wrapper


def auth_required(f):
    """
        Protects endpoints that require user authrorization for access
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return {
                "Status": 400,
                "Message": "Please provide a valid Authorization Header"
            }, 400

        auth_header = request.headers['Authorization']

        try:
            payload = auth_header.split(' ')[1]
        except IndexError:

            return {
                "Status": 400,
                "Message": "Please provide a valid Authorization Header"
            }, 400

        if not payload:
            return {
                "Status": 400,
                "Message": "Token is empty. Please provide a valid token"
            }, 400

        try:
            user_identity = UserModel.decode_auth_token(payload)
            global current_user, get_raw_auth
            get_raw_auth = payload
            current_user = UserModel.get_by_name(user_identity)

        except:
            return {
                "Status": 400,
                "Message": "Invalid Token. Please provide a valid token"
            }, 400

        return f(current_user, *args, **kwargs)
    return wrapper


def get_auth_identity():
    return current_user
