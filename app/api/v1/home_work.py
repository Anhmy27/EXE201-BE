from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from shortuuid import uuid
from sqlalchemy import asc, desc

from sqlalchemy_pagination import paginate

from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import db, Product, TypeProduct, PurchasedCourses, SessionCourse, UserDoHomeWork, HomeWork, User, \
    UserAnswer, Answer
from app.utils import escape_wildcard
from app.validator import ProductSchema, QueryParamsSchema, CourseSchema, SessionCourseSchema, UserDoHomeWorkSchema, \
    HomeWorkSchema, HomeWorkDetailSchema

api = Blueprint('home_work', __name__)


@api.route("/<product_id>", methods=["GET"])
@authorization_require('user')
def danh_sach_bai_tap(product_id):
    try:
        item = Product.query.filter(Product.id == product_id, Product.is_delete.is_(False)).first()
        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")
        data = ProductSchema(many=False, exclude=["files"]).dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))


### Thống kê lần làm bài tập user
@api.route("/<home_work_id>/data", methods=["GET"])
@authorization_require('user')
def chi_tiet_bai_tap(home_work_id):
    try:
        item = HomeWork.query.filter(HomeWork.id == home_work_id).first()

        if item is None:
            return send_error(message="Sản phẩm không tồn tại, F5 lại web")
        data = HomeWorkSchema(many=False, exclude=["questions"]).dump(item)
        return send_result(data=data)
    except Exception as ex:
        return send_error(message=str(ex))


@api.route("/<home_work_id>/session", methods=["GET"])
@authorization_require('user')
def get_session(home_work_id):
    try:
        page = int(request.args.get('page', 1))

        check = HomeWork.query.filter(HomeWork.id == home_work_id).first()
        if check is None:
            return send_error(message='Bài tập không tồn tại')

        user_id = get_jwt_identity()
        query = (UserDoHomeWork.query.filter(UserDoHomeWork.home_work_id == home_work_id,
                                             UserDoHomeWork.user_id == user_id)
                 .order_by(desc(UserDoHomeWork.created_date)))

        paginator = paginate(query, page, 20)

        data = UserDoHomeWorkSchema(many=True).dump(paginator.items)

        response_data = dict(
            items=data,
            total_pages=paginator.pages if paginator.pages > 0 else 1,
            total=paginator.total,
            # current_page=paginator.page,  # Số trang hiện tại
            has_previous=paginator.has_previous,  # Có trang trước không
            has_next=paginator.has_next  # Có trang sau không
        )

        return send_result(data=response_data)
    except Exception as ex:
        return send_error(message=str(ex))


# Tạo lượt làm bài
@api.route('/<home_work_id>', methods=['POST'])
@authorization_require('user')
def add_to_session(home_work_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return send_error(message='Người dùng không hợp lệ.')

        check = HomeWork.query.filter(HomeWork.id == home_work_id).first()
        if check is None:
            return send_error(message='Bài tập không tồn tại')

        session = UserDoHomeWork(id=str(uuid()), user_id=user_id, home_work_id=home_work_id)
        db.session.add(session)
        db.session.flush()
        db.session.commit()
        return send_result(data={"id": session.id}, message='Thành công.')
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


# Lấy câu hỏi

@api.route("/session/<session_id>", methods=["GET"])
@authorization_require('user')
def get_session_user(session_id):
    try:
        user_id = get_jwt_identity()

        check = UserDoHomeWork.query.filter_by(id=session_id).first()
        if check is None:
            return send_error(message='Lỗi')
        is_congratulation = False
        if check.is_congratulation:
            is_congratulation = True
            check.is_congratulation = False
            db.session.flush()
            db.session.commit()

        homework = HomeWork.query.filter_by(id=check.home_work_id).first()
        if homework is None:
            return send_error(message="Sản phẩm không tồn tại")

        # Lấy tất cả UserAnswer của user với các câu hỏi của bài này
        question_ids = [q.id for q in homework.questions]
        answers = UserAnswer.query.filter(
            UserAnswer.user_id == user_id,
            UserAnswer.user_do_home_work_id == session_id,
            UserAnswer.question_id.in_(question_ids)
        ).all()

        question_user_answers = {ua.question_id: ua.answer_id for ua in answers}

        schema = HomeWorkDetailSchema(many=False)
        schema.context = {
            "user_id": user_id,
            "question_user_answers": question_user_answers  # truyền vào context
        }

        data = schema.dump(homework)

        return send_result(data={
            "data": data,
            "status": check.status,
            "score": check.score,
            "is_congratulation": is_congratulation
        })

    except Exception as ex:
        return send_error(message=str(ex))


@api.route("/session/<session_id>", methods=["POST"])
@authorization_require('user')
def submit_session_user(session_id):
    try:
        user_id = get_jwt_identity()

        json_body = request.get_json()

        check = UserDoHomeWork.query.filter(UserDoHomeWork.id == session_id, UserDoHomeWork.status == False).first()
        if check is None:
            return send_error(message='Phiên không hợp lệ')
        home_work = HomeWork.query.filter(HomeWork.id == check.home_work_id).first()
        if home_work is None:
            return send_error(message="Bài tập không tồn tại")

        UserAnswer.query.filter(UserAnswer.user_do_home_work_id == session_id).delete()
        db.session.flush()

        result = json_body.get('result', [])

        score = 0

        for item in result:

            question_id = item['question_id']
            answer_id = item['answer_id']

            correct_answer = db.session.query(Answer).filter(Answer.question_id == question_id,
                                                             Answer.result_answer == True).first()

            if correct_answer and correct_answer.id == answer_id:
                score += 1

            new_user_answer = UserAnswer(id=str(uuid()), user_do_home_work_id=check.id,
                                         user_id=user_id, question_id=question_id, answer_id=answer_id)
            db.session.add(new_user_answer)
            db.session.flush()


        check.status = True
        check.score = score

        if score > home_work.len_question/2:
            check.is_congratulation = True
        db.session.commit()
        return send_result(message='Nộp bài thành công')
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))
