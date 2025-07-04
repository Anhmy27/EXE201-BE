from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy import asc, desc

from sqlalchemy_pagination import paginate

from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import db, User, Orders
from app.utils import escape_wildcard
from app.validator import OrderSchema, QueryParamsOrderSchema

api = Blueprint('order', __name__)

@api.route("/<order_id>", methods=["GET"])
@authorization_require('user')
def get_item(order_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không tồn tại.')
        item = Orders.query.filter(Orders.id == order_id, Orders.user_id==user_id).first()
        if item is None:
            return send_error(message="Đơn hàng không tồn tại, F5 lại web")
        data = OrderSchema().dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))

@api.route("", methods=["GET"])
@authorization_require('user')
def get_items():
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không tồn tại.')
        try:
            params = request.args.to_dict(flat=True)
            params = QueryParamsOrderSchema().load(params) if params else dict()
        except ValidationError as err:
            return send_error(message='INVALID_PARAMETERS_ERROR', data=err.messages)
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        order_by = params.get('order_by', 'created_date')
        sort = params.get('sort', 'desc')
        status = params.get('status', None)
        text_search = params.get('text_search', None)

        query = Orders.query.filter(Orders.user_id==user_id)
        if status:
            query = query.filter(Orders.status==status)

        if text_search:
            text_search = text_search.strip()
            text_search = text_search.lower()
            text_search = escape_wildcard(text_search)
            text_search = "%{}%".format(text_search)
            query = query.filter(Orders.id.ilike(text_search))

        column_sorted = getattr(Orders, order_by)

        query = query.order_by(desc(column_sorted)) if sort == "desc" else query.order_by(asc(column_sorted))

        paginator = paginate(query, page, page_size)

        orders = OrderSchema(many=True).dump(paginator.items)

        response_data = dict(
            items=orders,
            total_pages=paginator.pages if paginator.pages > 0 else 1,
            total=paginator.total,
            has_previous=paginator.has_previous,
            has_next=paginator.has_next
        )
        return send_result(data=response_data)
    except Exception as ex:
        return send_error(message=str(ex))
