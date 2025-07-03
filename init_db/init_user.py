import json
import os
import shortuuid
from faker import Faker
import random
import json

from shortuuid import uuid

fake = Faker("vi_VN")

import pandas as pd
from flask import Flask
from sqlalchemy import func

from app.models import User
from app.extensions import db
from app.settings import DevConfig
import datetime
from pytz import timezone
import random

CONFIG = DevConfig


def get_datetime_now():
    """
    Returns the current datetime in Asia/Ho_Chi_Minh timezone.
    """
    time_zone_sg = timezone('Asia/Ho_Chi_Minh')
    return datetime.datetime.now(time_zone_sg)


class Worker:
    def __init__(self):
        app = Flask(__name__)
        app.config.from_object(CONFIG)
        db.app = app
        db.init_app(app)
        app_context = app.app_context()
        app_context.push()

    def init_user(self):
        try:
            list_user = [
                {'email': f"{user.get('email')}", 'password': '123456789', 'full_name': f"{user.get('full_name')}",
                 'phone': f"0{random.randint(3200000000, 3999999999)}",
                 'gender': random.choice([0, 1]), 'is_admin': True,
                 'birthday': fake.date_of_birth(minimum_age=14, maximum_age=60)
                 }
                for user in [{'email': 'minhdocong2001@gmail.com', 'full_name': 'Minh Công'}]
            ]

            list_user.extend([
                {'email': f'{user}user@gmail.com', 'password': '123456789', 'full_name': f'{user} User',
                 'phone': f"0{random.randint(3200000000, 3999999999)}",
                 'gender': random.choice([0, 1]),
                 'birthday': fake.date_of_birth(minimum_age=14, maximum_age=60)
                 }
                for user in ['cuong', 'loc', 'tuan', 'ngoc_anh']
            ])

            list_user.extend([
                {'email': f"{fake.user_name()}{random.randint(1000, 9999)}@gmail.com",
                 "phone": f"0{random.randint(3200000000, 3999999999)}", 'gender': random.choice([0, 1]),
                 'birthday': fake.date_of_birth(minimum_age=14, maximum_age=60),
                 "password": "123456789", "full_name": fake.name()}
                for _ in range(1000)
            ])

            users_to_insert = []
            for item in list_user:
                item["id"] = str(uuid())
                item["is_active"] = True

                users_to_insert.append(item)

            db.session.bulk_insert_mappings(User, users_to_insert)
            db.session.commit()


        except Exception as ex:
            print(f"Lỗi: {ex}")

    def delete_user(self):
        User.query.filter().delete()
        db.session.commit()


if __name__ == '__main__':
    print("=" * 10, f"Starting init Address to the database on the uri: {CONFIG.SQLALCHEMY_DATABASE_URI}", "=" * 10)
    worker = Worker()
    worker.delete_user()
    worker.init_user()
    print("=" * 50, "Add address Success", "=" * 50)
