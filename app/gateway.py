from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.api.helper import send_error
from app.models import User  # Cập nhật đúng path tới model User


def authorization_require(author='user'):
    """
    Validate authorization follow permission user, admin, or all.
    Args:
        author (str): 'user' | 'admin' | 'all'
    Returns:
        Function decorator
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            user = User.query.filter_by(id=identity).first()

            if not user:
                return send_error(message='User không tồn tại')

            if author == 'admin' and user.is_admin:
                return fn(*args, **kwargs)
            elif author == 'user' and not user.is_admin:
                return fn(*args, **kwargs)
            elif author == 'all':
                return fn(*args, **kwargs)

            return send_error(message='BẠN KHÔNG CÓ QUYỀN')

        return decorator

    return wrapper
