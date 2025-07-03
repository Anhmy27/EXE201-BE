# coding: utf-8
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from app.enums import DURATION_SESSION_MINUTES, TYPE_FILE_LINK
from app.extensions import db
from app.utils import get_timestamp_now


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100, collation="utf8mb4_vietnamese_ci"), nullable=False)
    phone = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Boolean, default=0, nullable=False)  # 0: Nữ, # 1: Nam
    full_name = db.Column(db.String(100, collation="utf8mb4_vietnamese_ci"), nullable=False)
    avatar_id = db.Column(db.String(50), db.ForeignKey('files.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=True)
    avatar = db.relationship("Files", viewonly=True)

    birthday = db.Column(db.DATE, nullable=False)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    is_deleted = db.Column(db.Boolean, default=0)
    is_active = db.Column(db.Boolean, default=0)  # 1: Mở tài khoản , 0: Khóa tài khoản
    status = db.Column(db.Boolean, default=1)  # 1: Kích hoạt, 0: Không kích hoạt
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class Files(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.String(50), primary_key=True)
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255, collation="utf8mb4_vietnamese_ci"), nullable=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


class FileLink(db.Model):
    __tablename__ = "file_link"

    # TYPE_FILE_LINK = {
    #     'USER': 'user',
    #     'PRODUCT': 'product',
    #     'ORDER_REPORT': 'order_report',
    # }
    id = db.Column(db.String(50), primary_key=True)
    file_id = db.Column(db.String(50), db.ForeignKey('files.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    table_id = db.Column(db.String(50), nullable=True)
    table_type = db.Column(db.String(50), nullable=False)

    index = db.Column(db.Integer, nullable=True, default=0)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


class VerityCode(db.Model):
    __tablename__ = 'verity_code'

    id = db.Column(db.String(50), primary_key=True)
    code = db.Column(db.String(20))
    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)
    limit = db.Column(INTEGER(unsigned=True), nullable=True)  # Cho phép NULL
    user = db.relationship('User', viewonly=True)


class TypeProduct(db.Model):
    __tablename__ = 'type_product'
    id = db.Column(db.String(50), primary_key=True)
    key = db.Column(db.Text)
    name = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    describe = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    type_product_id = db.Column(db.String(50), db.ForeignKey('type_product.id', ondelete='SET NULL',
                                                             onupdate='CASCADE'), nullable=True)
    is_delete = db.Column(db.Boolean, nullable=False, default=False)
    price = db.Column(db.BigInteger, nullable=True, default=0)
    type_product = db.relationship('TypeProduct', lazy=True)

    created_date = db.Column(db.Integer,
                             default=get_timestamp_now())
    modified_date = db.Column(db.Integer,
                              default=get_timestamp_now())

    files = db.relationship(
        'Files',
        secondary='file_link',
        primaryjoin=(
            "and_(Product.id == FileLink.table_id, FileLink.table_type == 'product')"
        ),
        secondaryjoin="FileLink.file_id == Files.id",
        lazy='dynamic',
        order_by="asc(FileLink.index)",
        viewonly=True
    )

    home_works = db.relationship('HomeWork', backref='product', cascade='all, delete-orphan', lazy=True,
                                 order_by='HomeWork.created_date.asc()')

    session_courses = db.relationship('SessionCourse', backref='product', cascade='all, delete-orphan', lazy=True,
                                 order_by='SessionCourse.created_date.asc()')

    doc_course = db.relationship('DocCourse', backref='product', cascade='all, delete-orphan', lazy=True,
                                      order_by='DocCourse.created_date.asc()')


class DocCourse(db.Model):
    __tablename__ = 'doc_course'

    id = db.Column(db.String(50), primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=True)

    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255, collation="utf8mb4_vietnamese_ci"), nullable=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)

class HomeWork(db.Model):
    __tablename__ = 'home_work'

    id = db.Column(db.String(50), primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=True)
    name = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    description = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    questions = db.relationship('Question', backref='home_work', cascade='all, delete-orphan', lazy=True,
                                order_by='Question.created_date.asc()')

    @property
    def len_question(self):
        return len(self.questions) if self.questions else 0


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.String(50), primary_key=True)
    question = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=True)

    home_work_id = db.Column(db.String(50), db.ForeignKey('home_work.id', ondelete='CASCADE', onupdate='CASCADE'),
                             nullable=True)

    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    answers = db.relationship('Answer', backref='question', cascade='all, delete-orphan', lazy=True,
                              order_by='Answer.created_date.asc()')


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.String(50), primary_key=True)
    question_id = db.Column(db.String(50), db.ForeignKey('question.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=True)
    answer = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    result_answer = db.Column(db.Boolean, nullable=False, default=False)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())


class UserDoHomeWork(db.Model):
    __tablename__ = 'user_do_home_work'

    id = db.Column(db.String(50), primary_key=True)

    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)

    home_work_id = db.Column(db.String(50), db.ForeignKey('home_work.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)

    status = db.Column(db.Boolean, default=False) # Submit / not Submit

    score =  db.Column(INTEGER(unsigned=True), default=0)

    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())

    is_congratulation = db.Column(db.Boolean, default=False)



class UserAnswer(db.Model):
    __tablename__ = 'user_answer'
    id = db.Column(db.String(50), primary_key=True)

    user_do_home_work_id = db.Column(db.String(50), db.ForeignKey('user_do_home_work.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)

    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)

    question_id = db.Column(db.String(50), db.ForeignKey('question.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=True)

    answer_id = db.Column(db.String(50), db.ForeignKey('answer.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=True)

    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    question = db.relationship("Question", viewonly=True)
    answer = db.relationship("Answer", viewonly=True)

class SessionCourse(db.Model):
    __tablename__ = 'session_course'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    url = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    file_name = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='SET NULL', onupdate='SET NULL'),
                           nullable=True)

    file_id = db.Column(db.String(50), db.ForeignKey('files.id', ondelete='SET NULL', onupdate='SET NULL'),
                           nullable=True)

    file =  db.relationship("Files", viewonly=True)



class CartItems(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.String(50), primary_key=True)
    created_date = db.Column(db.Integer, default=get_timestamp_now())
    modified_date = db.Column(db.Integer, default=get_timestamp_now())
    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=True)
    product = db.relationship("Product", viewonly=True)


class SessionOrderCartItems(db.Model):
    __tablename__ = 'session_order_cart_items'
    id = db.Column(db.String(50), primary_key=True)
    created_date = db.Column(db.Integer, default=get_timestamp_now())
    cart_id = db.Column(db.String(50), db.ForeignKey('cart_items.id', ondelete='CASCADE',
                                                     onupdate='CASCADE'), nullable=False)
    session_order_id = db.Column(db.String(50), db.ForeignKey('session_order.id', ondelete='CASCADE',
                                                              onupdate='CASCADE'), nullable=False)
    cart_detail = relationship('CartItems', viewonly=True)


class SessionOrder(db.Model):
    __tablename__ = 'session_order'

    id = db.Column(db.String(50), primary_key=True)
    created_date = db.Column(db.Integer, default=get_timestamp_now())
    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)
    duration = db.Column(db.Integer, default=lambda: get_timestamp_now() + DURATION_SESSION_MINUTES * 60)
    items = db.relationship('SessionOrderCartItems', lazy=True,
                            order_by="asc(SessionOrderCartItems.created_date)")
    is_delete = db.Column(db.Boolean, default=False)


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)
    count = db.Column(db.BigInteger, nullable=True, default=0)
    created_date = db.Column(db.Integer, default=get_timestamp_now())
    modified_date = db.Column(db.Integer, default=get_timestamp_now())
    items = db.relationship('PurchasedCourses', lazy=True,
                            order_by="asc(PurchasedCourses.created_date)")
    payment_online_id = db.Column(db.String(50),
                                  db.ForeignKey('payment_online.id', ondelete='SET NULL', onupdate='SET NULL'))

    payment_online = db.relationship("PaymentOnline", viewonly=True)
    user = db.relationship('User', viewonly=True)


class PaymentOnline(db.Model):
    __tablename__ = 'payment_online'
    id = db.Column(db.String(50), primary_key=True)
    order_payment_id = db.Column(db.String(100), nullable=False)
    request_payment_id = db.Column(db.String(50), nullable=False)

    session_order_id = db.Column(
        db.String(50),
        db.ForeignKey('session_order.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True  # Cho phép NULL
    )

    result_payment = db.Column(db.JSON, nullable=True, default=None)
    status_payment = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(20), nullable=True)  # momo / zalo
    created_date = db.Column(db.Integer, default=get_timestamp_now())


class PurchasedCourses(db.Model):
    __tablename__ = 'purchased_courses'
    id = db.Column(db.String(50), primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.id', ondelete='SET NULL', onupdate='SET NULL'),
                           nullable=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.id', ondelete='CASCADE', onupdate='CASCADE'),
                         nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=True)

    price = db.Column(db.BigInteger, nullable=True, default=0)

    created_date = db.Column(db.Integer, default=get_timestamp_now())
    modified_date = db.Column(db.Integer, default=get_timestamp_now())
    product = db.relationship("Product", viewonly=True)
    user = db.relationship('User', viewonly=True)
