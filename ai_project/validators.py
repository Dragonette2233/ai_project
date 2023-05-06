from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, ValidationError
from werkzeug.utils import secure_filename
import secrets

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    file = FileField('Photo')
    
    def validate_file(form, field):
        if field.data:
            filename = secure_filename(field.data.filename)
            if not any([filename.endswith('.jpg'), filename.endswith('.jpeg'), filename.endswith('.png')]):
                raise ValidationError('Only jpg, jpeg and png files are allowed.')
            

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
