import datetime
import pickle
from typing import List
from flask import jsonify
from flask_jwt_extended import decode_token, get_jwt_identity, verify_jwt_in_request_optional
from flask_mail import Message as MessageMail
from jinja2 import Template

from app.extensions import mail
from app.settings import DevConfig

CONFIG = DevConfig



def get_user_id_request():
    user_id = None
    try:
        verify_jwt_in_request_optional()  # Không bắt buộc token
        user_id = get_jwt_identity()
    except Exception:
        pass
    return user_id

def send_result(data: any = None, message_id: str = '', message: str = "OK", code: int = 200,
                status: str = 'success', show: bool = False, duration: int = 0, is_dynamic: bool = False):
    """
    Args:
        data: simple result object like dict, string or list
        message: message send to client, default = OK
        code: code default = 200
        version: version of api
    :param data:
    :param message_id:
    :param message:
    :param code:
    :param status:
    :param show:
    :param duration:
    :return:
    json rendered sting result
    """
    message_dict = {
        "id": message_id,
        "text": message,
        "status": status,
        "show": show,
        "duration": duration,
        "dynamic": is_dynamic
    }

    res = {
        "code": code,
        "data": data,
        "message": message_dict,
        "version": get_version(CONFIG.VERSION)
    }

    return jsonify(res), 200


def send_error(data: any = None, message_id: str = '', message: str = "Error", code: int = 400,
               status: str = 'error', show: bool = False, duration: int = 0,
               is_dynamic: bool = False):
    """

    :param data:
    :param message_id:
    :param message:
    :param code:
    :param status:
    :param show:
    :param duration:
    :return:
    """
    message_dict = {
        "id": message_id,
        "text": message,
        "status": status,
        "show": show,
        "duration": duration,
        "dynamic": is_dynamic
    }

    res = {
        "code": code,
        "data": data,
        "message": message_dict,
        "version": get_version(CONFIG.VERSION)
    }

    return jsonify(res), code


def get_version(version: str) -> str:
    """
    if version = 1, return api v1
    version = 2, return api v2
    Returns:

    """
    version_text = f"FIT APIs v{version}"
    return version_text


def send_email(recipient: str, title: str, body: str) -> None:
    """
    send email with flask mail
    :param recipient:
    :param title:
    :param body:
    :return:
    """
    msg = MessageMail(title, recipients=[recipient])
    msg.html = body
    # Try to send the email.
    try:
        mail.send(msg)
    except Exception as ex:
        print(ex)


# The old function using smtp gmail
def send_email_template_old(recipient: str, title: str, template: str, data_fill: object):
    """
    send email with by template
    :param recipient:
    :param title:
    :param template:
    :param data_fill:
    :return: bool
    """
    try:
        template = Template(template)
        body = template.render(data_fill)  # fill data for template html
        send_email(recipient, title, body)  # send email
    except Exception as e:
        print(e.__str__())


def convert_to_datetime(date_str):
    try:
        # Chuyển chuỗi thành datetime với định dạng "dd/MM/yyyy"
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # Trả về None nếu định dạng không đúng
        return None


def send_email_template(recipient: str, title: str, template: str, data_fill: object, cc_recipient: str = ''):
    """
    send email with by template
    :param recipient:
    :param cc_recipient:
    :param title:
    :param template:
    :param data_fill:
    :return: bool
    """
    try:
        template = Template(template)
        body = template.render(data_fill)  # fill data for template html
        # send_email_aws(recipient=recipient, title=title, body=body)  # send email
        send_email(recipient=recipient, title=title, body=body)
        return True
    except Exception as e:
        print(e.__str__())

    return False


def render_template(template, data):
    try:
        template = Template(template)
        return template.render(data)
    except Exception as e:
        print(e.__str__())
    return False


def paginator_mongodb(query, page, page_size, total):
    """ handle paginator mongodb

    :param query:
    :param page:
    :param page_size:
    :param total:
    :return: bool
    """
    if page <= 0:
        return False, None, None
    if page_size <= 0:
        return False, None, None
    items = query.skip((page - 1) * page_size).limit(page_size)
    total_pages = total / page_size
    if total % page_size != 0:
        total_pages = total_pages + 1
    return True, items, total, int(total_pages)