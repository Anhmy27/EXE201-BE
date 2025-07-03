from typing import Dict

from shortuuid import uuid
from flask import Blueprint, request
from sqlalchemy import asc, desc
from sqlalchemy_pagination import paginate

from app.enums import TYPE_FILE_LINK
from app.extensions import db
from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import Product, SessionCourse, HomeWork, Question
from app.utils import trim_dict, get_timestamp_now
from app.validator import SessionCourseSchema, SessionCourseValidation, HomeWorkSchema, HomeWorkValidation

api = Blueprint('manage/home_work', __name__)


@api.route('/<product_id>', methods=['POST'])
@authorization_require('admin')
def add_homework(product_id):
    try:
        product = Product.query.filter(Product.id == product_id).first()
        if product is None:
            return send_error(message='Khóa học không tồn tại.')

        json_req = request.get_json()
        json_body = trim_dict(json_req)
        validator_input = HomeWorkValidation()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        home_work = HomeWork(id=str(uuid()), **json_body, product_id = product_id)
        db.session.add(home_work)
        db.session.flush()
        db.session.commit()

        return send_result(data=HomeWorkSchema(many=False).dump(home_work) ,message='Thêm thành công.')

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

        HomeWork.query.filter(HomeWork.id.in_(list_id), HomeWork.product_id == product_id).delete()

        db.session.flush()
        db.session.commit()

        return send_result(message='Thành công')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route("/<product_id>/<home_work_id>", methods=["GET"])
def get_item(product_id, home_work_id):
    try:
        item = HomeWork.query.filter(HomeWork.product_id == product_id, HomeWork.id == home_work_id).first()
        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")
        data = HomeWorkSchema(many=False).dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))

@api.route("/<product_id>", methods=["GET"])
@authorization_require('admin')
def get_items(product_id):
    try:

        page = int(request.args.get('page', 1))

        query = (HomeWork.query.filter(HomeWork.product_id == product_id)
                .order_by(desc(HomeWork.created_date)))

        paginator = paginate(query, page, 20)

        sessions = HomeWorkSchema(many=True).dump(paginator.items)

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



