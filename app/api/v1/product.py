from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import asc, desc

from sqlalchemy_pagination import paginate

from app.api.helper import send_result, send_error
from app.models import db, Product, TypeProduct
from app.utils import escape_wildcard
from app.validator import ProductSchema, QueryParamsSchema

api = Blueprint('product', __name__)

@api.route("/<product_id>", methods=["GET"])
def get_item(product_id):
    try:
        item = Product.query.filter(Product.id == product_id, Product.is_delete.is_(False)).first()
        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")
        data = ProductSchema(many=False, exclude=["home_works"]).dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))

@api.route("", methods=["GET"])
def get_items():
    try:
        try:
            params = request.args.to_dict(flat=True)
            params = QueryParamsSchema().load(params) if params else dict()
        except ValidationError as err:
            return send_error(message='INVALID_PARAMETERS_ERROR', data=err.messages)
        from_money = params.get('from_money', None)
        to_money = params.get('to_money', None)
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        order_by = params.get('order_by', 'created_date')
        sort = params.get('sort', 'desc')
        text_search = params.get('text_search', None)
        select_type = params.get('select_type', [])

        query = Product.query.filter(Product.is_delete.is_(False))

        if select_type:
            query = query.filter(Product.type_product_id.in_(select_type))

        if text_search:
            text_search = text_search.strip()
            text_search = text_search.lower()
            text_search = escape_wildcard(text_search)
            text_search = "%{}%".format(text_search)
            query = query.filter(Product.name.ilike(text_search))
        if from_money:
            query = query.filter(Product.price >= from_money)

        if to_money:
            query = query.filter(Product.price <= to_money)

        column_sorted = getattr(Product, order_by)

        query = query.order_by(desc(column_sorted)) if sort == "desc" else query.order_by(asc(column_sorted))

        paginator = paginate(query, page, page_size)

        products = ProductSchema(many=True, exclude=["home_works"]).dump(paginator.items)

        response_data = dict(
            items=products,
            total_pages=paginator.pages if paginator.pages > 0 else 1,
            total=paginator.total,
            # current_page=paginator.page,  # Số trang hiện tại
            has_previous=paginator.has_previous,  # Có trang trước không
            has_next=paginator.has_next  # Có trang sau không
        )
        return send_result(data=response_data)
    except Exception as ex:
        return send_error(message=str(ex))

