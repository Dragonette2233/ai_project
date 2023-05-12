# from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
import secrets


def validate_no_cyrillic_chars(form, field):
    if any([ch for ch in field.data if 'а' <= ch <= 'я' or 'А' <= ch <= 'Я']):
        raise ValidationError('Пароль не должен содержать кириллицу')

def validate_file(filename):
    
    if filename == '':
        return 'default.jpg'

    if not any([filename.endswith('.jpg'), 
                filename.endswith('.jpeg'),
                filename.endswith('.png')]):
        
        return ('Only jpg, png, jpeg allowed', 'error')
        
    
    filetype = filename.split('.')[1]
    filename = secrets.token_urlsafe(16)
    return '.'.join((filename, filetype))
