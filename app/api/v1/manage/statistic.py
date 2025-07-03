import json
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy import cast, Integer, BigInteger, case, text, and_, extract
from dateutil.relativedelta import relativedelta
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import asc, desc, func

from app.api.helper import send_result, send_error
from app.extensions import db
from app.gateway import authorization_require
from app.models import TypeProduct, Product, Orders, User, PurchasedCourses, Files, FileLink
from app.validator import StatisticTop10CustomerSchema, StatisticTop5ProductSchema

api = Blueprint('statistic', __name__)


@api.route('', methods=['GET'])
@authorization_require('admin')
def statistic_all():
    try:
        data = {
            'user': User.query.filter(User.is_admin==False).count(),
            'product': Product.query.filter().count(),
            'orders': Orders.query.filter().count(),
        }

        return send_result(data=data, message="Thành công")
    except Exception as ex:
        return send_error(message=str(ex))

@api.route('/number_product_by_type', methods=['GET'])
@authorization_require('admin')
def get_number_product_by_type():
    try:

        data = [
            {
                "name": p.name,
                "total": Product.query.filter(
                    Product.type_product_id == p.id).count()
            }
            for p in TypeProduct.query.filter().order_by(asc(TypeProduct.key)).all()
        ]

        total_all = sum(item["total"] for item in data)

        data_statistic = {}

        total_percent = 0  # Tổng phần trăm đã tính trước mục cuối

        for index, item in enumerate(data):
            if total_all == 0:
                phan_tram = 0  # Tránh chia cho 0
            else:
                phan_tram = (item['total'] / total_all) * 100

            if index == len(data) - 1 and phan_tram > 0:
                data_statistic[item['name']] = 100 - total_percent  # Điều chỉnh mục cuối cùng
            else:
                data_statistic[item['name']] = round(phan_tram, 2)
                total_percent += data_statistic[item['name']]

        return send_result(data={'result': data_statistic, 'data_count': data}, message="Thành công")
    except Exception as ex:
        return send_error(message=str(ex))



@api.route('/top_customer', methods=['GET'])
@authorization_require('admin')
def top_customer():
    try:
        now_dt = datetime.now(timezone.utc)
        start_timestamp = int((now_dt - relativedelta(months=12)).timestamp())

        # Truy vấn top 10 user có tổng tiền orders lớn nhất trong 12 tháng gần nhất
        top_users = (
            db.session.query(
                User.id,
                User.full_name,
                User.email,
                Files.file_path,
                func.sum(PurchasedCourses.price).label("total_count")
            )
            .join(Orders, Orders.user_id == User.id)
            .join(PurchasedCourses, PurchasedCourses.order_id == Orders.id)
            .outerjoin(Files, Files.id == User.avatar_id)  # Outer join để tránh lỗi nếu không có avatar
            .filter(PurchasedCourses.created_date >= start_timestamp)
            .group_by(User.id, Files.file_path)  # Cần group cả file_path nếu có outer join
            .order_by(desc("total_count"))
            .limit(10)
            .all()
        )

        data = StatisticTop10CustomerSchema(many=True).dump(top_users)

        return send_result(data=data, message="Thành công")
    except Exception as ex:
        return send_error(message=str(ex))


@api.route('/revenue_and_sold_product_by_type', methods=['GET'])
@authorization_require('admin')
def get_number_by_type_product_6_month_ago():
    try:
        month = request.args.get('month', 12, type=int)

        now_dt = datetime.now(timezone.utc).replace(day=1)

        # Tạo danh sách 10 tháng gần nhất
        months = [(now_dt - relativedelta(months=i)).strftime("%m-%Y") for i in range(month)][::-1]

        # Lấy danh sách các loại sản phẩm
        type_products = TypeProduct.query.filter().order_by(asc(TypeProduct.key)).all()
        type_product_dict = {
            p.id: {"name": p.name, "list_id": [p.id]} for p in type_products
        }

        # Truy vấn dữ liệu từ PurchasedCourses
        query = (
            db.session.query(
                func.date_format(func.from_unixtime(PurchasedCourses.created_date), "%m-%Y").label("month"),
                Product.type_product_id,
                cast(func.count(PurchasedCourses.id), Integer).label("total_quantity"),
                cast(func.sum(PurchasedCourses.price), BigInteger).label("total_count")

            )
            .join(Product, PurchasedCourses.product_id == Product.id)
            .join(Orders, PurchasedCourses.order_id == Orders.id)
            .filter(PurchasedCourses.created_date >= int((now_dt - relativedelta(months=month-1)).timestamp()))
            .group_by("month", Product.type_product_id)
            .order_by("month")
        )

        # Xử lý dữ liệu
        sales_data = defaultdict(lambda: defaultdict(lambda: {"quantity": 0, "count": 0}))

        for row in query:
            month = row.month
            type_id = row.type_product_id
            quantity = row.total_quantity
            count = row.total_count

            # Gán dữ liệu vào danh sách tương ứng
            for type_key, type_value in type_product_dict.items():
                if type_id in type_value["list_id"]:
                    sales_data[type_value["name"]][month]["quantity"] += quantity
                    sales_data[type_value["name"]][month]["count"] += count

        # Chuyển đổi thành format JSON
        series_sold = [
            {
                "name": type_name,
                "data": [sales_data[type_name][month]["quantity"] for month in months],  # Lấy số lượng
            }
            for type_name in sales_data
        ]

        series_revue = [
            {
                "name": type_name,
                "data": [sales_data[type_name][month]["count"] for month in months],  # Lấy số lần bán (revue)
            }
            for type_name in sales_data
        ]

        # Kết quả JSON
        chart_data_sold = {
            "categories": months,
            "series": series_sold
        }

        chart_data_revenue = {
            "categories": months,
            "series": series_revue
        }

        return send_result(data={
            'chart_data_sold': chart_data_sold,
            'chart_data_revenue': chart_data_revenue,
            'month': month
        }, message="Thành công")

    except Exception as ex:
        return send_error(message=str(ex))


@api.route('/number_user_by_age_and_gender', methods=['GET'])
@authorization_require('admin')
def number_user_by_age_and_gender():
    try:
        today = func.curdate()  # Lấy ngày hiện tại từ MySQL

        age_expr = func.timestampdiff(text("YEAR"), User.birthday, today)

        stats = (
            db.session.query(
                case(
                    (age_expr < 20, "< 20"),
                    (age_expr.between(20, 39), "20-40"),
                    (age_expr.between(40, 59), "40-60"),
                    (age_expr >= 60, "> 60"),
                    else_="Unknown"
                ).label("age_group"),
                User.gender,
                func.count().label("count")
            )
            .group_by("age_group", User.gender)
            .all()
        )

        # Định nghĩa các danh mục tuổi
        categories = ["< 20", "20-40", "40-60", "> 60"]

        # Tạo dictionary để chứa dữ liệu
        age_gender_data = {
            "Nam": {cat: 0 for cat in categories},
            "Nữ": {cat: 0 for cat in categories}
        }

        # Duyệt qua kết quả thống kê và sắp xếp vào đúng nhóm
        for age_group, gender, count in stats:
            gender_key = "Nam" if gender == 1 else "Nữ"
            if age_group in age_gender_data[gender_key]:
                age_gender_data[gender_key][age_group] = count

        # Định dạng dữ liệu cho biểu đồ
        series_data = [
            {"name": "Nam", "data": [age_gender_data["Nam"][cat] for cat in categories]},
            {"name": "Nữ", "data": [age_gender_data["Nữ"][cat] for cat in categories]}
        ]

        return send_result(data={"series": series_data, "categories": categories}, message="Thành công")

    except Exception as ex:
        return send_error(message=str(ex))

@api.route('/top_product', methods=['GET'])
@authorization_require('admin')
def top_product():
    try:
        now_dt = datetime.now(timezone.utc)
        start_timestamp = int((now_dt - relativedelta(months=12)).timestamp())

        # Truy vấn top 5 product có lượt bán hot nhất trong 1 năm
        # Truy vấn top 5 sản phẩm bán chạy nhất trong 1 năm
        top_products = (
            db.session.query(
                Product.id,
                Product.name,
                func.coalesce(Files.file_path, "").label("file_path"),  # Lấy file đầu tiên
                func.count(PurchasedCourses.id).label("total_quantity")
            )
            .join(PurchasedCourses, PurchasedCourses.product_id == Product.id)
            .outerjoin(
                FileLink,
                and_(FileLink.table_id == Product.id, FileLink.table_type == "product", FileLink.index == 0)
                # Chỉ lấy index = 0
            )
            .outerjoin(Files, Files.id == FileLink.file_id)
            .filter(PurchasedCourses.created_date >= start_timestamp)
            .group_by(Product.id, Product.name, Files.file_path)  # Nhóm theo sản phẩm
            .order_by(desc("total_quantity"))
            .limit(5)
            .all()
        )

        data = StatisticTop5ProductSchema(many=True).dump(top_products)

        return send_result(data=data, message="Thành công")
    except Exception as ex:
        return send_error(message=str(ex))
