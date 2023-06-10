from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    TextAreaField, 
    FileField, 
    EmailField, 
    PasswordField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, EqualTo
from .validators import validate_no_cyrillic_chars, validate_file


class AuthUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), 
                                                     Length(min=6, max=32),
                                                     validate_no_cyrillic_chars])
    c_password = PasswordField('Confirm password', validators=[DataRequired(),
                                                               Length(min=6, max=32),
                                                               EqualTo('password', message='Пароль должен совпадать'),
                                                               ])
    submit = SubmitField('Регистрация')

class LoginUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=6, max=32),
                                                     validate_no_cyrillic_chars])
    submit = SubmitField('Войти')

class BlogPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=2, max=50)])
    body = TextAreaField('Содержание', validators=[DataRequired(), Length(min=2, max=400)])
    file = FileField('Фото (Не более 5МБ)', validators=[validate_file])