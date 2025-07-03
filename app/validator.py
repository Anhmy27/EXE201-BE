import json
import typing

from marshmallow import Schema, fields, validate, ValidationError, types, pre_load, validates_schema
from app.enums import TYPE_PAYMENT_ONLINE, TYPE_PAYMENT
from app.utils import REGEX_EMAIL, REGEX_PHONE_NUMBER


# Validator
class BaseValidation(Schema):

    def custom_validate(
            self,
            data: typing.Mapping,
            *,
            many: typing.Optional[bool] = None,
            partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> (bool, str):
        try:
            self._do_load(data, many=many, partial=partial, postprocess=False)
        except ValidationError as exc:
            check = typing.cast(typing.Dict[str, typing.List[str]], exc.messages)
            if hasattr(self, 'define_message'):
                for key in check:
                    if key in self.define_message:
                        return False, self.define_message[key]
                return False, 'INVALID_PARAMETERS_ERROR'
            else:
                # return check
                return False, 'INVALID_PARAMETERS_ERROR'

        return True, ''


def default_schema_get_search(sort_type):
    class GetSearchValidation(BaseValidation):
        page = fields.Integer(required=False)
        page_size = fields.Integer(required=False)
        search_name = fields.String(required=False, validate=validate.Length(min=0, max=200))

        sort = fields.String(required=False,
                             validate=validate.OneOf(sort_type))
        order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))

    return GetSearchValidation


class ChangePasswordValidation(BaseValidation):
    current_password = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=16, error="Mật khẩu hiện tại phải từ 1 đến 16 ký tự."),
        ],
        error_messages={"required": "Mật khẩu hiện tại không được để trống."}
    )

    new_password = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=16, error="Mật khẩu mới phải từ 1 đến 16 ký tự."),
        ],
        error_messages={"required": "Mật khẩu mới không được để trống."}
    )


class FileSchema(Schema):
    id = fields.String()
    file_path = fields.String()
    file_name = fields.String()
    created_date = fields.Integer()


class UserSchema(Schema):
    id = fields.String()
    email = fields.String()
    phone = fields.String()
    gender = fields.Boolean()
    full_name = fields.String()
    birthday = fields.Date()
    avatar = fields.Nested(FileSchema())
    created_date = fields.Integer()
    is_active = fields.Boolean()
    status = fields.Boolean()
    is_admin = fields.Boolean()


class StatisticTop10CustomerSchema(Schema):
    id = fields.Str()
    full_name = fields.Str()
    email = fields.Str()
    avatar = fields.Str()  # Đường dẫn avatar đã lấy từ Files.file_path
    total_count = fields.Int()


class StatisticTop5ProductSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    file_path = fields.Str()  # Đường dẫn avatar đã lấy từ Files.file_path
    total_quantity = fields.Int()


class AuthValidation(BaseValidation):
    password = fields.String(
        required=True,
        validate=[
            validate.Length(min=8, max=16, error="Mật khẩu phải từ 8 đến 16 ký tự.")
        ],
        error_messages={"required": "Mật khẩu không được để trống."}
    )

    email = fields.String(
        required=True,
        validate=[
            validate.Length(min=8, max=100, error="Email phải từ 8 đến 100 ký tự."),
            validate.Regexp(REGEX_EMAIL, error="Email không hợp lệ.")
        ],
        error_messages={"required": "Email không được để trống."})


class PasswordValidation(BaseValidation):
    current_password = fields.String(
        required=True,
        error_messages={"required": "Mật khẩu hiện tại không được để trống."}
    )

    new_password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=16, error="Mật khẩu mới phải từ 8 đến 16 ký tự.")],
        error_messages={"required": "Mật khẩu mới không được để trống."}
    )

    confirm_password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=16, error="Xác nhận mật khẩu phải từ 8 đến 16 ký tự.")],
        error_messages={"required": "Xác nhận mật khẩu không được để trống."}
    )


class RegisterValidation(BaseValidation):
    full_name = fields.String(required=True, error_messages={"required": "Họ và tên không được để trống."})

    password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=16, error="Mật khẩu phải có độ dài từ 8 đến 16 ký tự.")],
        error_messages={"required": "Mật khẩu không được để trống."}
    )

    confirm_password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=16, error="Xác nhận mật khẩu phải có độ dài từ 8 đến 16 ký tự.")],
        error_messages={"required": "Xác nhận mật khẩu không được để trống."}
    )

    email = fields.String(
        required=True,
        validate=[
            validate.Length(min=8, max=100, error="Email phải có từ 8 đến 100 ký tự."),
            validate.Regexp(REGEX_EMAIL, error="Email không hợp lệ.")
        ],
        error_messages={"required": "Email không được để trống."}
    )

    phone = fields.String(
        required=True,
        validate=[
            validate.Length(min=10, max=11, error="Số điện thoại phải có từ 10 đến 11 kí tự."),
            validate.Regexp(REGEX_PHONE_NUMBER, error="Số điện thoại không hợp lệ.")
        ],
        error_messages={"required": "Số điện thoại không được để trống."}
    )

    birthday = fields.String(
        required=True,
        error_messages={"required": "Ngày sinh không được để trống."}
    )


class UserValidation(BaseValidation):
    email = fields.String(allow_none=True)

    phone = fields.String(
        required=True,
        validate=[
            validate.Length(min=10, max=11, error="Số điện thoại phải có độ dài từ 10 đến 11 ký tự."),
            validate.Regexp(REGEX_PHONE_NUMBER, error="Số điện thoại không hợp lệ.")
        ],
        error_messages={"required": "Số điện thoại không được để trống."}
    )

    full_name = fields.String(
        required=True,
        error_messages={"required": "Họ và tên là bắt buộc."}
    )

    gender = fields.Boolean(
        required=True,
        error_messages={"required": "Giới tính là bắt buộc."}
    )

    birthday = fields.String(
        required=True,
        error_messages={"required": "Ngày sinh là bắt buộc."}
    )

    detail_address = fields.String(allow_none=True)

    address = fields.Dict(
        required=True,
        error_messages={"required": "Địa chỉ là bắt buộc."}
    )


class CartValidation(BaseValidation):
    product_id = fields.String(
        required=True,
        error_messages={"required": "Mã sản phẩm không được để trống."}
    )


class CartUpdateValidation(BaseValidation):
    quantity = fields.Integer(
        required=True,
        error_messages={"required": "Số lượng không được để trống."}
    )

    product_id = fields.String(
        required=True,
        error_messages={"required": "Mã sản phẩm không được để trống."}
    )


class TypeProductValidation(BaseValidation):
    key = fields.String(
        required=True,
        error_messages={"required": "Mã sản phẩm không được để trống."}
    )

    name = fields.String(
        required=True,
        error_messages={"required": "Tên sản phẩm không được để trống."}
    )


class ProductValidation(BaseValidation):
    files = fields.List(
        fields.Dict(
            keys=fields.Str(),
            values=fields.Raw(),
            validate=validate.Length(min=1, error="Dữ liệu tệp tin không được rỗng.")
        ),
        required=True,
        validate=validate.Length(min=1, error="Danh sách tệp tin phải chứa ít nhất một mục."),
        error_messages={"required": "Danh sách tệp tin không được để trống."}
    )

    price = fields.Float(
        required=True,
        error_messages={"required": "Giá gốc không được để trống."}
    )

    name = fields.String(
        required=True,
        error_messages={"required": "Tên sản phẩm không được để trống."}
    )

    describe = fields.String(
        allow_none=True
    )

    type_product_id = fields.String(
        allow_none=True
    )


class SessionCourseValidation(BaseValidation):
    sessions = fields.List(
        fields.Dict(
            keys=fields.Str(),
            values=fields.Raw(),
            validate=validate.Length(min=1, error="Dữ liệu tệp tin không được rỗng.")
        ),
        required=True,
        validate=validate.Length(min=1, error="Danh sách bài giảng phải chứa ít nhất một mục."),
        error_messages={"required": "Danh sách tệp tin không được để trống."}
    )


class HomeWorkValidation(BaseValidation):
    name = fields.String(
        required=True,
        error_messages={"required": "Tên không được để trống."}
    )

    description = fields.String(
        required=True,
        error_messages={"required": "Mô tả không được để trống."}
    )

class AnswerValidate(BaseValidation):
    answer = fields.Str(required=True, validate=validate.Length(min=1, error="Nội dung đáp án không được rỗng."))
    result_answer = fields.Bool(required=True)


class QuestionValidate(BaseValidation):
    question = fields.Str(required=True, validate=validate.Length(min=1, error="Nội dung không được rỗng."))

    answers = fields.List(
        fields.Nested(AnswerValidate),
        required=True,
        validate=validate.Length(min=1, error="Danh sách đáp án phải chứa ít nhất một mục."),
        error_messages={"required": "Danh sách đáp án không được để trống."}
    )

    @validates_schema
    def validate_correct_answer(self, data, **kwargs):
        answers = data.get('answers', [])
        if not any(ans.get('result_answer') for ans in answers):
            raise ValidationError("Phải có ít nhất một đáp án đúng.", field_name="answers")


class ProductUpdateValidation(BaseValidation):
    files = fields.List(
        fields.Dict(
            keys=fields.Str(),
            values=fields.Raw(),
            validate=validate.Length(min=1, error="Dữ liệu tệp tin không được rỗng.")
        ),
        required=True,
        validate=validate.Length(min=1, error="Danh sách tệp tin phải chứa ít nhất một mục."),
        error_messages={"required": "Danh sách tệp tin không được để trống."}
    )

    price = fields.Float(
        required=True,
        error_messages={"required": "Giá gốc không được để trống."}
    )

    name = fields.String(
        required=True,
        error_messages={"required": "Tên sản phẩm không được để trống."}
    )

    describe = fields.String(
        allow_none=True
    )

    type_product_id = fields.String(
        required=True,
        error_messages={"required": "Mã loại sản phẩm không được để trống."}
    )


class PaymentValidation(BaseValidation):
    payment_type = fields.String(
        required=True,
        validate=validate.OneOf(
            choices=TYPE_PAYMENT_ONLINE.values(),
            error="Loại thanh toán chỉ được là 'momo' hoặc 'zalo'."
        ),
        error_messages={"required": "Loại thanh toán không được để trống."}
    )


class SessionOrderValidate(BaseValidation):
    payment_type = fields.String(
        required=True,
        validate=validate.OneOf(
            choices=TYPE_PAYMENT.values(),
            error="Hình thức thanh toán phải là 'cod', 'momo' hoặc 'zalo'."
        ),
        error_messages={"required": "Hình thức thanh toán không được để trống."}
    )

    payment_online_id = fields.String(
        allow_none=True
    )

    @validates_schema
    def validate_payment_online_id(self, data, **kwargs):
        if data.get('payment_type') in TYPE_PAYMENT_ONLINE.values() and not data.get('payment_online_id'):
            raise ValidationError(
                "Mã giao dịch thanh toán online bắt buộc khi phương thức thanh toán là 'momo' hoặc 'zalo'.",
                field_name='payment_online_id')


class TypeProductSchema(Schema):
    id = fields.String()
    key = fields.String()
    name = fields.String()


class SessionCourseSchema(Schema):
    id = fields.String()
    file_name = fields.String()
    file_id = fields.String()
    name = fields.String()
    created_date = fields.Integer()
    file = fields.Nested(FileSchema)

class AnswerSchema(Schema):
    id = fields.String()
    answer = fields.String()
    result_answer = fields.Boolean()


class QuestionSchema(Schema):
    id = fields.String()
    question = fields.String()
    created_date = fields.Integer()
    answers = fields.List(fields.Nested(AnswerSchema))


class HomeWork2Schema(Schema):
    id = fields.String()
    name = fields.String()
    len_question = fields.Integer()
    description = fields.String()
    questions = fields.List(fields.Nested(QuestionSchema))


class UserDoHomeWorkSchema(Schema):
    id = fields.String()
    created_date = fields.Integer()
    modified_date = fields.Integer()
    status = fields.Boolean()
    score = fields.Integer()
    len_question = fields.Integer()


class DocSchema(Schema):
    id = fields.String()
    file_path = fields.String()
    file_name = fields.String()
    created_date = fields.Integer()

class ProductSchema(Schema):
    id = fields.String()
    price = fields.Integer()
    name = fields.String()
    describe = fields.String()
    type_product = fields.Nested(TypeProductSchema)
    files = fields.List(fields.Nested(FileSchema()))
    created_date = fields.Integer()
    modified_date = fields.Integer()
    home_works = fields.List(fields.Nested(HomeWork2Schema(only=("id", "name", "description", "len_question"))))
    session_courses = fields.List(fields.Nested(SessionCourseSchema))
    doc_course = fields.List(fields.Nested(DocSchema))

    class Meta:
        ordered = True


class HomeWorkSchema(Schema):
    id = fields.String()
    name = fields.String()
    len_question = fields.Integer()
    description = fields.String()
    questions = fields.List(fields.Nested(QuestionSchema))
    product = fields.Nested(ProductSchema(only=("id", "name")))


class AnswerSchema2(Schema):
    id = fields.String()
    answer = fields.String()
    result_answer = fields.Boolean()


class QuestionSchema2(Schema):
    id = fields.String()
    question = fields.String()
    created_date = fields.Integer()
    answers = fields.List(fields.Nested(AnswerSchema2))
    user_answer_id = fields.Method("get_user_answer_id")

    def get_user_answer_id(self, obj):
        question_user_answers = self.context.get("question_user_answers", {})
        return question_user_answers.get(obj.id)


class HomeWorkDetailSchema(Schema):
    id = fields.String()
    name = fields.String()
    len_question = fields.Integer()
    description = fields.String()
    questions = fields.List(fields.Nested(QuestionSchema2))
    product = fields.Nested(ProductSchema(only=("id", "name")))

class CourseSchema(Schema):
    id = fields.String()
    name = fields.String()
    describe = fields.String()
    type_product = fields.Nested(TypeProductSchema)
    files = fields.List(fields.Nested(FileSchema()))
    created_date = fields.Integer()
    modified_date = fields.Integer()

    class Meta:
        ordered = True


class QueryParamsSchema(BaseValidation):
    from_money = fields.Integer(allow_none=True, validate=validate.Range(min=0))  # Có thể None, không nhỏ hơn 0
    to_money = fields.Integer(allow_none=True, validate=validate.Range(min=0))  # Có thể None, nhưng không nhỏ hơn 0
    page = fields.Integer(required=True, validate=validate.Range(min=1))  # Bắt buộc, không nhỏ hơn 1
    page_size = fields.Integer(missing=10,
                               validate=validate.Range(min=1, max=100))  # Mặc định là 10, giới hạn tối đa 100
    order_by = fields.String(missing="created_date")  # Mặc định là 'created_date'
    sort = fields.String(
        missing="desc", validate=validate.OneOf(["asc", "desc"])  # Chỉ chấp nhận 'asc' hoặc 'desc'
    )
    text_search = fields.String(allow_none=True)  # Có thể None
    select_type = fields.List(fields.String(), allow_none=True)

    @pre_load
    def parse_select_type(self, data, **kwargs):
        """Tự động convert select_type từ string JSON thành list"""
        if "select_type" in data and isinstance(data["select_type"], str):
            try:
                data["select_type"] = json.loads(data["select_type"])
            except json.JSONDecodeError:
                raise ValidationError({"select_type": "Invalid JSON format."})
        return data

    @pre_load
    def normalize_empty_strings_and_trim(self, data, **kwargs):
        for key in ['text_search', 'from_money', 'to_money']:
            if key in data:
                value = data[key]
                if isinstance(value, str):
                    value = value.strip()
                    data[key] = value if value != '' else None
        return data


class QueryParamsAllSchema(BaseValidation):
    page = fields.Integer(required=True, validate=validate.Range(min=1))  # Bắt buộc, không nhỏ hơn 1
    page_size = fields.Integer(missing=10,
                               validate=validate.Range(min=1, max=100))  # Mặc định là 10, giới hạn tối đa 100
    order_by = fields.String(missing="created_date")  # Mặc định là 'created_date'
    sort = fields.String(
        missing="desc", validate=validate.OneOf(["asc", "desc"])  # Chỉ chấp nhận 'asc' hoặc 'desc'
    )
    text_search = fields.String(allow_none=True)


class QueryParamsOrderSchema(BaseValidation):
    page = fields.Integer(required=True, validate=validate.Range(min=1))  # Bắt buộc, không nhỏ hơn 1
    page_size = fields.Integer(missing=10,
                               validate=validate.Range(min=1, max=100))  # Mặc định là 10, giới hạn tối đa 100
    order_by = fields.String(missing="created_date")  # Mặc định là 'created_date'
    sort = fields.String(
        missing="desc", validate=validate.OneOf(["asc", "desc"])  # Chỉ chấp nhận 'asc' hoặc 'desc'
    )
    status = fields.String(validate=validate.OneOf(["pending", "processing", "delivering", "resolved"]))
    text_search = fields.String(allow_none=True)
    time = fields.String()


class CartSchema(Schema):
    id = fields.String()
    product = fields.Nested(ProductSchema(only=("id", "price", "name",
                                                "describe", "files", "type_product")))
    created_date = fields.Integer()
    modified_date = fields.Integer()
    quantity = fields.Integer()


class CartDetailSchema(Schema):
    id = fields.String()
    product = fields.Nested(ProductSchema(only=("id", "price", "name", "files")))


class SessionOrderCartItemSchema(Schema):
    id = fields.String()
    cart_detail = fields.Nested(CartDetailSchema(only=("id", "product")))


class SessionSchema(Schema):
    id = fields.String()
    items = fields.List(fields.Nested(SessionOrderCartItemSchema))
    created_date = fields.Integer()
    duration = fields.Integer()


class PurchasedCoursesSchema(Schema):
    id = fields.String()
    product = fields.Nested(ProductSchema(only=("id", "name", "files", "type_product")))
    created_date = fields.Integer()
    price = fields.Integer()


class PaymentOnlineSchema(Schema):
    id = fields.String()
    order_payment_id = fields.String()
    request_payment_id = fields.String()
    session_order_id = fields.String()
    result_payment = fields.Dict(allow_none=True)
    status_payment = fields.Boolean()
    type = fields.String()
    created_date = fields.Integer()


class OrderSchema(Schema):
    id = fields.String()
    count = fields.Float()
    created_date = fields.Integer()
    items = fields.List(fields.Nested(PurchasedCoursesSchema))
    payment_online = fields.Nested(PaymentOnlineSchema(only=("id", "status_payment", "type", "created_date")))
    user = fields.Nested(UserSchema(only=("id", "email", "full_name")))
