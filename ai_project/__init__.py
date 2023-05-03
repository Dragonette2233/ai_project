from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
import os


DB_NAME = "database.db"


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///{DB_NAME}'.format(DB_NAME=DB_NAME),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER = os.path.join(app.static_folder, 'post_photos'),
        UPLOAD_ROUTE = os.path.join(app.static_url_path, 'post_photos')
    )

    from .views import bp as views
    from .auth import bp as auth
    from .blog import bp as blog
    from .models import db, User

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

    return app
