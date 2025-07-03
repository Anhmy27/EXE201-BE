import os

from shortuuid import uuid

from flask import Blueprint, request, send_file

from werkzeug.utils import secure_filename

from app.api.helper import send_result, send_error, CONFIG
from app.gateway import authorization_require
from app.models import db, Files, Product, FileLink, DocCourse

api = Blueprint('file', __name__)

FILE_ORIGIN = "app"

FOLDER = "/files/image_project/"

FOLDER_MP4 = "/files/mp4/"

FOLDER_DOC = "/doc/"

@api.route('upload_file', methods=['POST'])
def upload_one_file():
    try:
        # Lấy file từ request (chỉ lấy file đầu tiên từ input 'file')
        file = request.files.get('file')  # Chỉ nhận một file
        if not file:
            return send_error(message="No file provided")

        # Lấy tên file và phần mở rộng
        filename, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.lower()

        # Danh sách các định dạng hợp lệ
        allowed_extensions = ['.jpg', '.jpeg', '.png']

        if file_extension not in allowed_extensions:
            return send_error(message="Chỉ chấp nhận  định dạng JPG, JPEG, và PNG.")

        # Tạo UUID làm tên file an toàn
        id_file = str(uuid())
        file_name = secure_filename(id_file) + file_extension

        if not os.path.exists(FILE_ORIGIN + FOLDER):
            os.makedirs(FILE_ORIGIN + FOLDER)
        file_path = FILE_ORIGIN + FOLDER + file_name
        file.save(os.path.join(file_path))
        file = Files(id=id_file, file_path=FOLDER + file_name)
        db.session.add(file)
        db.session.commit()
        dt = {
            "file_path": file.file_path,
            "id": file.id,
        }

        return send_result(data=dt, message="File uploaded successfully")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))



@api.route('upload', methods=['POST'])
def upload_multi_file():
    try:
        files = request.files.getlist('files')  # Nhận danh sách file từ 'files'
        if not files:
            return send_error(message="No files provided")
        allowed_extensions = ['.jpg', '.jpeg', '.png']

        # Tạo danh sách để lưu thông tin các file đã upload
        uploaded_files = []
        for file in files:
            try:
                filename, file_extension = os.path.splitext(file.filename)

                file_extension = file_extension.lower()

                if file_extension not in allowed_extensions:
                    continue

                id_file = str(uuid())
                file_name = secure_filename(id_file) + file_extension
                if not os.path.exists(FILE_ORIGIN+FOLDER):
                    os.makedirs(FILE_ORIGIN+FOLDER)
                file_path = FILE_ORIGIN + FOLDER + file_name
                file.save(os.path.join(file_path))

                file = Files(id=id_file, file_path=FOLDER + file_name)
                db.session.add(file)
                db.session.commit()
            except Exception:
                continue
            dt = {
                "file_path": file.file_path,
                "id": file.id,
            }
            uploaded_files.append(dt)

        return send_result(data=uploaded_files, message="Ok")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))

@api.route('/<file_id>', methods=['GET'])
def get_picture(file_id):
    try:
        file = Files.query.filter(Files.id == file_id).first()
        if file is None:
            return send_error(message='File not found')
        file = os.path.abspath(file.file_path)
        return send_file(file, as_attachment=True)
    except Exception as ex:
        return send_error(message=str(ex))


@api.route('upload_doc/<product_id>', methods=['POST'])
def upload_doc_file(product_id):
    try:
        product = Product.query.filter(Product.id == product_id).first()

        if product is None:
            return send_error(message='Khóa học không tồn tại')

        # Lấy file từ request (chỉ lấy file đầu tiên từ input 'file')
        file = request.files.get('file')  # Chỉ nhận một file
        if not file:
            return send_error(message="No file provided")

        # Lấy tên file và phần mở rộng
        filename, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.lower()

        # Danh sách các định dạng hợp lệ
        allowed_extensions = ['.pdf']

        if file_extension not in allowed_extensions:
            return send_error(message="Chỉ chấp nhận định dạng PDF.")

        # Tạo UUID làm tên file an toàn
        id_file = str(uuid())
        file_name = secure_filename(filename) + file_extension


        if not os.path.exists(FILE_ORIGIN + FOLDER_DOC + f"{product_id}"):
            os.makedirs(FILE_ORIGIN + FOLDER_DOC + f"{product_id}")
        file_path = FILE_ORIGIN + FOLDER_DOC + f"{product_id}/" + secure_filename(filename) + id_file + file_extension
        file.save(os.path.join(file_path))
        file_db = DocCourse(id=id_file, file_path=FOLDER + file_name, file_name=file_name, product_id=product_id)
        db.session.add(file_db)
        db.session.flush()

        db.session.commit()
        dt = {
            "file_path": file_db.file_path,
            "id": file_db.id,
            "file_name": file_db.file_name,
        }

        return send_result(data=dt, message="Upload thành công")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))

@api.route('download/<file_id>', methods=['GET'])
def download_doc_file(file_id):
    try:
        # Tìm file trong DB
        file = DocCourse.query.filter_by(id=file_id).first()
        if not file:
            return send_error(message="File không tồn tại.")

        # Đường dẫn tuyệt đối
        absolute_path = os.path.join(FILE_ORIGIN, file.file_path)

        if not os.path.exists(absolute_path):
            return send_error(message="Không tìm thấy file trên server.")

        # Trả file về trình duyệt
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=file.file_name,
            mimetype='application/pdf'
        )
    except Exception as ex:
        return send_error(message=str(ex))


@api.route('doc/<file_id>', methods=['DELETE'])
@authorization_require('admin')
def delete_file(file_id):
    try:
        # Tìm file trong DB
        DocCourse.query.filter_by(id=file_id).delete()
        db.session.flush()
        db.session.commit()
        return send_result(message="Xóa thành công")


    except Exception as ex:
        return send_error(message=str(ex))


@api.route('mp4', methods=['POST'])
@authorization_require('admin')
def upload_file_mp4():
    try:
        # Lấy file từ request (chỉ lấy file đầu tiên từ input 'file')
        file = request.files.get('file')  # Chỉ nhận một file
        if not file:
            return send_error(message="No file provided")

        # Lấy tên file và phần mở rộng
        filename, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.lower()

        # Danh sách các định dạng hợp lệ
        allowed_extensions = ['.mp4']

        if file_extension not in allowed_extensions:
            return send_error(message="Chỉ chấp nhận mp4.")

        # Tạo UUID làm tên file an toàn
        id_file = str(uuid())
        file_name = secure_filename(filename) + file_extension

        if not os.path.exists(FILE_ORIGIN + FOLDER_MP4):
            os.makedirs(FILE_ORIGIN + FOLDER_MP4)
        file_path = FILE_ORIGIN + FOLDER_MP4 + secure_filename(id_file) + file_extension
        file.save(os.path.join(file_path))
        mp4 = Files(id=id_file, file_path=FOLDER_MP4 +
                                          secure_filename(id_file) + file_extension, file_name=file_name)
        db.session.add(mp4)
        db.session.commit()
        dt = {
            "file_name": mp4.file_name,
            "file_id": mp4.id,
        }

        return send_result(data=dt, message="File uploaded successfully")
    except Exception as ex:
        db.session.rollback()
        return send_error(message=str(ex))