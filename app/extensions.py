from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .settings import DevConfig
CONFIG = DevConfig

jwt = JWTManager()

# init SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

# email
mail = Mail()
