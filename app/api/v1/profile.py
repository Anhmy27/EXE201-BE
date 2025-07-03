from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.enums import  GROUP_KEY_PARAM
from app.api.helper import get_user_id_request
from app.api.helper import send_error, send_result
from app.extensions import db
from app.gateway import authorization_require
from app.models import User
from app.utils import trim_dict

from app.validator import UserSchema, UserValidation

api = Blueprint('profile', __name__)


@api.route('', methods=['GET'])
@authorization_require('user')
def profile():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    data = UserSchema().dump(user)

    if user.is_admin:
        data['param_router'] = GROUP_KEY_PARAM.get("is_admin", '/')
    else:
        data['param_router'] = GROUP_KEY_PARAM.get("user", '/')
    return send_result(data=data)


@api.route('', methods=['PUT'])
@authorization_require('all')
def update_profile():
    try:
        user_id = get_jwt_identity()
        json_req = request.get_json()
        json_body = trim_dict(json_req)
        validator_input = UserValidation()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message="Người dùng không hợp lệ")

        for key, value in json_body.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        db.session.flush()
        db.session.commit()
        data =  UserSchema().dump(user)
        data.setdefault('param_router', GROUP_KEY_PARAM.get(user.group.key, '/'))

        return send_result(data=data, message='Thành công')
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route('/update_avatar', methods=['PUT'])
@authorization_require('user')
def update_avatar():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return send_error(message='Nguười dùng không tồn tại')

    body_request = request.get_json()

    avatar_id = body_request.get('avatar_id')
    if avatar_id is None:
        return send_error(message='Chưa chọn file')
    user.avatar_id = avatar_id
    db.session.commit()

    data = UserSchema().dump(user)

    return send_result(data=data)



