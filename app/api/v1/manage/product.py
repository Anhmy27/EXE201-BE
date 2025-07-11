from shortuuid import uuid
from flask import Blueprint, request

from app.enums import TYPE_FILE_LINK
from app.extensions import db
from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import Product, FileLink
from app.utils import trim_dict, get_timestamp_now
from app.validator import ProductValidation, ProductUpdateValidation

api = Blueprint('manage/product', __name__)


@api.route('', methods=['POST'])
@authorization_require('admin')
def new():
    try:

        json_req = request.get_json()
        json_body = trim_dict(json_req)
        validator_input = ProductValidation()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        files = json_body.pop('files')

        product = Product(**json_body, id=str(uuid()))
        db.session.add(product)
        db.session.flush()


        file_objects = [FileLink(id=str(uuid()), table_id=product.id, file_id=file["id"],
                                 table_type=TYPE_FILE_LINK.get('PRODUCT', 'product'),
                                 index=index, created_date=get_timestamp_now()+index)
                        for index, file in enumerate(files)]
        db.session.bulk_save_objects(file_objects)
        db.session.flush()
        db.session.commit()

        return send_result(message='Thành công')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


def check_coincided_name_product(name='', product_id=''):
    existed_name = Product.query.filter(Product.name == name)
    if product_id:
        existed_name = existed_name.filter(Product.id != product_id)
    if existed_name.first() is None:
        return False
    return True



@api.route("", methods=["DELETE"])
@authorization_require('admin')
def remove_item():
    try:
        body_request = request.get_json()
        list_id = body_request.get('list_id', [])
        if len(list_id) == 0:
            return send_error(message='Chưa chọn item nào.')
        Product.query.filter(Product.id.in_(list_id)).update({"is_delete": True}, synchronize_session=False)
        db.session.flush()
        db.session.commit()
        return send_result(message="Xóa sản phẩm thành công")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))


@api.route("/<product_id>", methods=["PUT"])
@authorization_require('admin')
def update_item(product_id):
    try:

        product = Product.query.filter(Product.id == product_id, Product.is_delete.is_(False)).first()
        if product is None:
            return send_error(message='Sản phẩm không tồn tại.')

        json_req = request.get_json()
        json_body = trim_dict(json_req)
        validator_input = ProductUpdateValidation()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        files = json_body.pop('files')

        for key, value in json_body.items():
            if hasattr(product, key):
                setattr(product, key, value)
        FileLink.query.filter(FileLink.table_id==product.id,
                              FileLink.table_type==TYPE_FILE_LINK.get('PRODUCT', 'product')).delete()
        db.session.flush()

        file_objects = [FileLink(id=str(uuid()), table_id=product.id, file_id=file["id"],
                                 table_type=TYPE_FILE_LINK.get('PRODUCT', 'product'),
                                 index=index, created_date=get_timestamp_now() + index)
                        for index, file in enumerate(files)]
        db.session.bulk_save_objects(file_objects)
        db.session.flush()
        db.session.commit()

        return send_result(message="Cập nhật sản phẩm thành công.")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))
