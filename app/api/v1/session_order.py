from shortuuid import uuid
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.helper import send_result, send_error
from app.enums import TYPE_PAYMENT_ONLINE
from app.gateway import authorization_require
from app.models import db, User, SessionOrder, SessionOrderCartItems, Orders, PurchasedCourses, CartItems, PaymentOnline
from app.utils import get_timestamp_now, trim_dict
from app.validator import SessionSchema, SessionOrderValidate

api = Blueprint('session_order', __name__)


@api.route('', methods=['POST'])
@authorization_require('user')
def add_item_to_session():
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không hợp lệ.')
        json_body = request.get_json()

        list_cart_id = json_body.get('list_cart_id', [])

        if len(list_cart_id) == 0:
            return send_error(message='Chưa chọn sản phẩm thanh toán.')

        session = SessionOrder(id=str(uuid()), user_id=user_id)
        db.session.add(session)
        db.session.flush()


        list_session_order_cart = [SessionOrderCartItems(id=str(uuid()),cart_id=cart_id,
                                                         session_order_id=session.id)
                                   for index, cart_id in enumerate(list_cart_id)]

        db.session.bulk_save_objects(list_session_order_cart)
        db.session.flush()
        db.session.commit()
        return send_result(data= {"id": session.id} ,message='Thành công.')
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route("/<session_id>", methods=["GET"])
@authorization_require('user')
def get_items_in_session(session_id):
    try:
        user_id=get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không hợp lệ.')
        session = SessionOrder.query.filter(SessionOrder.user_id==user_id, SessionOrder.id == session_id,
                                          SessionOrder.duration > get_timestamp_now(), SessionOrder.is_delete == False
                                            ).first()
        if session is None:
            return send_error(message='Phiên thanh toán đã hết hạn')
        items = session.items


        total = sum(item.cart_detail.product.price for item in items)

        session_data = SessionSchema().dump(session)
        session_data.update({
            'total': total,
        })
        return send_result(data=session_data)
    except Exception as ex:
        return send_error(message=str(ex))

@api.route("/<session_id>", methods=["POST"])
@authorization_require('user')
def order_session(session_id):
    try:
        user_id=get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không hợp lệ.')
        session_order = SessionOrder.query.filter(SessionOrder.user_id == user_id, SessionOrder.id == session_id,
                                                        SessionOrder.duration > get_timestamp_now(),
                                                        SessionOrder.is_delete == False).first()

        if session_order is None:
            return send_error(message='Phiên thanh toán đã hết hạn')

        json_request = request.get_json()

        json_body = trim_dict(json_request)
        validator_input = SessionOrderValidate()
        is_not_validate = validator_input.validate(json_body)
        if is_not_validate:
            return send_error(data=is_not_validate, message='Validate Error')

        payment_type = json_body.get('payment_type')
        payment_online_id = json_body.get('payment_online_id', None)
        if payment_type in  TYPE_PAYMENT_ONLINE.values():
            payment_online = PaymentOnline.query.filter_by(id=payment_online_id).first()
            if payment_online is None:
                return send_error(message='Không tìm thấy thanh toán trước đó.')


        order = Orders(id=str(uuid()), user_id=user_id)

        db.session.add(order)
        db.session.flush()

        items = session_order.items
        count = 0
        for index, item in enumerate(items):

            price = item.cart_detail.product.price

            order_item = PurchasedCourses(id=str(uuid()), user_id=user_id, created_date=get_timestamp_now()+index, order_id=order.id,
                                          product_id=item.cart_detail.product_id, price=price)
            db.session.add(order_item)
            CartItems.query.filter(CartItems.id==item.cart_id).delete()
            db.session.flush()
            count += price
        order.count = count
        session_order.is_delete = True
        if payment_type in  TYPE_PAYMENT_ONLINE.values():
            order.payment_status = True
            order.payment_online_id = payment_online_id

        db.session.flush()
        db.session.commit()

        return send_result(message='Đặt hàng thành công.', data={'count': count})
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))




