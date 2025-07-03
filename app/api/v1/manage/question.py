from typing import Dict

from numpy.ma.core import product
from shortuuid import uuid
from flask import Blueprint, request
from sqlalchemy import asc, desc
from sqlalchemy_pagination import paginate

from app.enums import TYPE_FILE_LINK
from app.extensions import db
from app.api.helper import send_result, send_error
from app.gateway import authorization_require
from app.models import Product, SessionCourse, HomeWork, Question, Answer
from app.utils import trim_dict, get_timestamp_now
from app.validator import SessionCourseSchema, SessionCourseValidation, HomeWorkSchema, HomeWorkValidation, \
    QuestionValidate

api = Blueprint('manage/question', __name__)


@api.route('/<home_work_id>', methods=['POST'])
@authorization_require('admin')
def add_question(home_work_id):
    try:
        home_work = HomeWork.query.filter(HomeWork.id == home_work_id).first()
        if home_work is None:
            return send_error(message='Khóa học không tồn tại.')

        json_req = request.get_json()
        data = json_req.get('data', [])

        for index, item in enumerate(data):

            validator_input = QuestionValidate()
            is_not_validate = validator_input.validate(item)
            if is_not_validate:
                continue

            question =  item.get('question')
            answers  = item.get('answers', [])

            new_question =  Question(id=str(uuid()), question=question, product_id=home_work.product.id,
                                     home_work_id=home_work.id, created_date=get_timestamp_now() + index)
            db.session.add(new_question)
            db.session.flush()

            for k,  answer in enumerate(answers):
                new_answers = Answer(id=str(uuid()), question_id=new_question.id, **answer, created_date=get_timestamp_now() + k )
                db.session.add(new_answers)
                db.session.flush()


        home_work = HomeWork.query.filter(HomeWork.id == home_work_id).first()

        db.session.commit()

        return send_result(data=HomeWorkSchema(many=False).dump(home_work) ,message='Thêm thành công.')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)


@api.route('/<question_id>', methods=['DELETE'])
@authorization_require('admin')
def remove(question_id):
    try:

        Question.query.filter(Question.id == question_id).delete()
        db.session.flush()
        db.session.commit()

        return send_result(message='Thành công')

    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex), code=442)



