from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "uTasker.db"
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uTasker@App|2024!'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'dev.mattt@gmail.com'
    app.config['MAIL_PASSWORD'] = 'wizw tgsm nilb wrxj'
    app.config['MAIL_DEFAULT_SENDER'] = 'dev.mattt@gmail.com'
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .views import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    from .models import User
    
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app
