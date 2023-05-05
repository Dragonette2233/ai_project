from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler
import logging
import os


DB_NAME = "database.db"


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///{DB_NAME}'.format(DB_NAME=DB_NAME),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER = os.path.join(app.instance_path, 'post_photos'),
        UPLOAD_ROUTE = os.path.join(app.instance_path, 'post_photos')
    )

    from .views import bp as views
    from .auth import bp as auth
    from .blog import bp as blog
    from .models import db, User

    # Logging configuration

    app.logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Removing consol logs
    for handler in app.logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            app.logger.removeHandler(handler)

    migrate = Migrate(app, db)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(blog, url_prefix='/blog')

    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.sign_in'
    # login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):

        return User.query.get(int(id))

    with app.app_context():
        db.create_all()

    @app.route('/greet')
    def index():
        app.logger.debug('Debug message')
        app.logger.info('Info message')
        app.logger.warning('Warning message')
        app.logger.error('Error message')
        app.logger.critical('Critical message')
        return 'Hello, world!'

    return app
