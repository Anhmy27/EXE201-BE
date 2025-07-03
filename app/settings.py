import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

class Config(object):
    SECRET_KEY = '3nF3Rn0'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

class DevConfig(Config):
    """Development configuration."""

    # mysql config
    TIME_ZONE = 'Asia/Ho_Chi_Minh'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BK_HOST_MYSQL = "127.0.0.1"
    BK_PORT_MYSQL = 3306
    BK_USERNAME_MYSQL = "root"
    BK_PASSWORD_MYSQL = "123456"
    BK_DBNAME_MYSQL = "bankhoahoc"
    SQLALCHEMY_DATABASE_URI = (
        f'mysql://{BK_USERNAME_MYSQL}:{BK_PASSWORD_MYSQL}'
        f'@{BK_HOST_MYSQL}:{BK_PORT_MYSQL}/{BK_DBNAME_MYSQL}?charset=utf8mb4'
    )

    # app config
    ENV = "dev"
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    TEMPLATES_AUTO_RELOAD = False
    HOST = '0.0.0.0'

    # version
    VERSION = "1.23.46"

    # JWT Config
    JWT_SECRET_KEY = '1234567a@'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    

    # email config
    ADMIN_EMAIL = "cn.company.enterprise@gmail.com"
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = "cn.company.enterprise@gmail.com"
    MAIL_PASSWORD = "gmve beaj gvgc juqb"
    MAIL_DEFAULT_SENDER = "cn.company.enterprise@gmail.com"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # website url
    BASE_URL_WEBSITE = "https://bc76-2402-800-61c7-eebd-b97e-c2b4-f019-2456.ngrok-free.app"

    # rabbitmq
    ENABLE_RABBITMQ_CONSUMER = False  # or True if needed
    SEND_MAIL_QUEUE = "send_mail_queue"
    SEND_MAIL_ROUTING_KEY = "send.mail"

    EXCHANGE_NAME = "default_exchange"
    EXCHANGE_TYPE = "direct"

    HOST_RABBIT = "localhost"
    PORT_RABBIT = 5672
    USER_RABBIT = "admin"
    PASSWORD_RABBIT = "admin"



