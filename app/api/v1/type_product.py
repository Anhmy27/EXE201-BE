from operator import or_

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import asc, desc
from app.api.helper import send_result, send_error
from app.models import TypeProduct
from app.utils import escape_wildcard
from app.validator import TypeProductSchema, QueryParamsAllSchema

api = Blueprint('type_product', __name__)


@api.route("", methods=["GET"])
def get_all_type():
    try:
        try:
            params = request.args.to_dict(flat=True)
            params = QueryParamsAllSchema().load(params) if params else dict()
        except ValidationError as err:
            return send_error(message='INVALID_PARAMETERS_ERROR', data=err.messages)

        order_by = params.get('order_by', 'name')
        sort = params.get('sort', 'asc')
        text_search = params.get('text_search', None)

        query = TypeProduct.query.filter()

        if text_search:
            text_search = text_search.strip()
            text_search = text_search.lower()
            text_search = escape_wildcard(text_search)
            text_search = "%{}%".format(text_search)

            query = query.filter(
                or_(
                    TypeProduct.name.ilike(f"%{text_search}%"),
                    TypeProduct.key.ilike(f"%{text_search}%")
                )
            )

        column_sorted = getattr(TypeProduct, order_by)

        query = query.order_by(desc(column_sorted)) if sort == "desc" else query.order_by(asc(column_sorted))


        type_products = TypeProductSchema(many=True).dump(query.all())

        return send_result(data=type_products)
    except Exception as ex:
        return send_error(message=str(ex))