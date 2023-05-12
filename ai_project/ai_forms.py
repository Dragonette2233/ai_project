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
from .validators import validate_no_cyrillic_chars


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
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    file = FileField('Photo')
    
    def validate_file(form, field):
        if field.data:
            filename = secure_filename(field.data.filename)
            if not any([filename.endswith('.jpg'), filename.endswith('.jpeg'), filename.endswith('.png')]):
                raise ValidationError('Only jpg, jpeg and png files are allowed.')