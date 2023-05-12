from sqlalchemy.sql import func
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150))
    openai_api = db.Column(db.LargeBinary())
    notes = db.relationship("Note")
    chathistory = db.relationship("AiHistory")
    imghistory = db.relationship("ImgHistory")
    # blog = db.relationship("Blog")


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Blog(db.Model):
    __tablename__ = "blog"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    title = db.Column(db.String(1000))
    body = db.Column(db.String(10000))
    photo = db.Column(db.String(10000), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    
class AiHistory(db.Model):
    __tablename__ = "chathistory"

    id = db.Column(db.Integer, primary_key=True)
    ask = db.Column(db.String(10000))
    output = db.Column(db.String(20000))
    output_success = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class ImgHistory(db.Model):
    __tablename__ = "imghistory"

    id = db.Column(db.Integer, primary_key=True)
    url_1 = db.Column(db.String(10000))
    url_2 = db.Column(db.String(10000))
    url_3 = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
