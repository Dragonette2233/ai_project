# from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from werkzeug.utils import secure_filename
import secrets


def validate_no_cyrillic_chars(form, field):
    if any([ch for ch in field.data if 'а' <= ch <= 'я' or 'А' <= ch <= 'Я']):
        raise ValidationError('Пароль не должен содержать кириллицу')

def validate_file(form, field):
        
        if field.data:
            filename = secure_filename(field.data.filename)
            if not any([filename.endswith('.jpg'), 
                        filename.endswith('.jpeg'), 
                        filename.endswith('.png')]):
                raise ValidationError('Only jpg, jpeg and png files are allowed.')
        else:
            field.data.filename = 'default.jpg'