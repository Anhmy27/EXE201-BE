from shortuuid import uuid
from datetime import date

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import desc, asc, and_
from sqlalchemy_pagination import paginate
from sqlalchemy import or_

from app.extensions import db
from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import User
from app.utils import escape_wildcard
from app.validator import QueryParamsAllSchema, UserSchema

api = Blueprint('manage/user', __name__)


@api.route('/<user_id>', methods=['GET'])
@authorization_require('admin')
def profile_user(user_id):

    user = User.query.filter_by(id=user_id).first()
    data = UserSchema().dump(user)
    return send_result(data=data)



@api.route("/active/<user_id>", methods=["PUT"])
@authorization_require('admin')
def active_user(user_id):
    try:
        user = User.query.filter(User.id == user_id).first()
        if not user:
            return send_error(message="Người dùng không tồn tại!")

        # Đảo trạng thái active
        user.is_active = not user.is_active
        db.session.flush()
        db.session.refresh(user)
        db.session.commit()

        # Xác định trạng thái mở/khoá
        status = "mở" if user.is_active else "khóa"
        return send_result(message=f"Tài khoản {user.email} đã được {status}.")

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))


@api.route("/customer", methods=["GET"])
@authorization_require('admin')
def get_customer():
    try:
        try:
            params = request.args.to_dict(flat=True)
            params = QueryParamsAllSchema().load(params) if params else dict()
        except ValidationError as err:
            return send_error(message='INVALID_PARAMETERS_ERROR', data=err.messages)


        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        order_by = params.get('order_by', 'created_date')
        sort = params.get('sort', 'desc')
        text_search = params.get('text_search', None)

        query = User.query.filter_by(is_admin=False)

        if text_search:
            text_search = text_search.strip()
            text_search = text_search.lower()
            text_search = escape_wildcard(text_search)
            text_search = "%{}%".format(text_search)

            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{text_search}%"),
                    User.email.ilike(f"%{text_search}%")
                )
            )


        column_sorted = getattr(User, order_by)

        query = query.order_by(desc(column_sorted)) if sort == "desc" else query.order_by(asc(column_sorted))

        paginator = paginate(query, page, page_size)

        customers = UserSchema(many=True).dump(paginator.items)

        response_data = dict(
            items=customers,
            total_pages=paginator.pages if paginator.pages > 0 else 1,
            total=paginator.total,
            has_previous=paginator.has_previous,
            has_next=paginator.has_next
        )
        return send_result(data=response_data)
    except Exception as ex:
        return send_error(message=str(ex))


@api.route("", methods=["DELETE"])
@authorization_require('admin')
def remove_item():
    try:
        body_request = request.get_json()
        list_id = body_request.get('list_id', [])
        if len(list_id) == 0:
            return send_error(message='Chưa chọn item nào.')
        User.query.filter(User.id.in_(list_id)).delete()
        db.session.flush()
        db.session.commit()
        return send_result(message="Xóa thành công")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))


