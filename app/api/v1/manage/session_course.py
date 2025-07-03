from typing import Dict

from shortuuid import uuid
from flask import Blueprint, request
from sqlalchemy import asc, desc
from sqlalchemy_pagination import paginate

from app.enums import TYPE_FILE_LINK
from app.extensions import db
from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import Product, SessionCourse
from app.utils import trim_dict, get_timestamp_now
from app.validator import ProductValidation, ProductSchema, SessionCourseSchema, SessionCourseValidation

api = Blueprint('manage/session_course', __name__)


@api.route('/<product_id>', methods=['POST'])
@authorization_require('admin')
def add_session(product_id):
    try:
        product = Product.query.filter(Product.id == product_id).first()
        if product is None:
            return send_error(message='Khóa học không tồn tại.')

        json_req = request.get_json()
        json_body = trim_dict(json_req)
        validator_input = SessionCourseValidation()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        sessions = json_body.get('sessions', [])

        new_sessions = []
        for i, s in enumerate(sessions):
            if isinstance(s, Dict):
                new_session = SessionCourse(
                    id=str(uuid()),
                    created_date=get_timestamp_now() + i,
                    product_id=product_id,
                    **s
                )
                new_sessions.append(new_session)
        db.session.bulk_save_objects(new_sessions)
        db.session.flush()
        db.session.commit()

        return send_result(message='Thêm thành công.')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route('/<product_id>', methods=['DELETE'])
@authorization_require('admin')
def remove(product_id):
    try:
        product = Product.query.filter(Product.id == product_id).first()
        if product is None:
            return send_error(message='Khóa học không tồn tại.')

        body_request = request.get_json()
        list_id = body_request.get('list_id', [])
        if len(list_id) == 0:
            return send_error(message='Chưa chọn item nào.')

        SessionCourse.query.filter(SessionCourse.id.in_(list_id), SessionCourse.product_id == product_id).delete()

        db.session.flush()
        db.session.commit()

        return send_result(message='Thành công')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route("/<product_id>/<session_id>", methods=["GET"])
@authorization_require('admin')
def get_item(product_id, session_id):
    try:
        item = SessionCourse.query.filter(SessionCourse.product_id == product_id, SessionCourse.id == session_id).first()
        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")
        data = SessionCourseSchema(many=False).dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))


@api.route("/<session_id>", methods=["PUT"])
@authorization_require('admin')
def put_item(session_id):
    try:
        item = SessionCourse.query.filter(SessionCourse.id == session_id).first()

        json_req = request.get_json()
        json_body = trim_dict(json_req)

        name = json_body.get('name')
        file_name = json_body.get('file_name')
        file_id = json_body.get('file_id')

        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")

        item.name = name
        item.file_id = file_id
        item.file_name= file_name

        db.session.flush()
        db.session.commit()

        data = SessionCourseSchema(many=False).dump(item)
        return send_result(data=data, message='Cập nhật thành công')
    except Exception as ex:
        return send_error(message=str(ex))

@api.route("/<product_id>", methods=["GET"])
@authorization_require('admin')
def get_items(product_id):
    try:

        page = int(request.args.get('page', 1))

        query = (SessionCourse.query.filter(SessionCourse.product_id == product_id)
                .order_by(desc(SessionCourse.created_date)))

        paginator = paginate(query, page, 20)

        sessions = SessionCourseSchema(many=True).dump(paginator.items)

        response_data = dict(
            items=sessions,
            total_pages=paginator.pages if paginator.pages > 0 else 1,
            total=paginator.total,
            has_previous=paginator.has_previous,  # Có trang trước không
            has_next=paginator.has_next  # Có trang sau không
        )
        return send_result(data=response_data)
    except Exception as ex:
        return send_error(message=str(ex))



