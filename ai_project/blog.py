from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    current_app,
    send_from_directory,
    jsonify
)

from flask_login import login_required, current_user
from .validators import validate_file
from .models import User, Blog, db
from .ai_forms import BlogPostForm
from markupsafe import escape
import os

bp = Blueprint("blog", __name__)

def get_post(id, check_author=True, is_all=False):
    
    if id is None:
        return None

    post = Blog.query.filter_by(id=id).first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != current_user.id:
        abort(403)
    
    return post


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
   
    posts = Blog.query.join(User).order_by(Blog.created.desc()).all()
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/image/<string:filename>')
@login_required
def get_image(filename):
    
    post_route = os.path.join(current_app.instance_path, 'post_photos/')
    
    return send_from_directory(post_route, filename)


@bp.errorhandler(413)
def handle_request_entity_too_large(error):
    # flash('Вы пытаетесь загрузить слишком большой файл, превышающий 5МБ', category='error')
    return 'Cлишком большой файл'


@bp.route('/<int:id>/<string:state>', methods=('GET', 'POST',))
@bp.route('/<string:state>', methods=('GET', 'POST',))
@login_required
def create_update(error=None, id=None, state=None):
    
    post = get_post(id)
    form = BlogPostForm(body=post.body if post else '')
    
    if request.method == 'POST' and form.validate_on_submit():
        
        title = form.title.data
        body = form.body.data
        file = form.file.data

        print(file.filename)
        
        if state == 'create' and file.filename != 'default.jpg':
            save_post_photo(file=file)
            
        elif state == 'update' and file.filename != 'default.jpg':
            delete_post_photo(filename=post.photo)
            save_post_photo(file=file)

        if state == 'update':
            
            Blog.query.filter_by(id=id).update(
                    {
                        Blog.title: title,
                        Blog.body: body,
                        Blog.photo: file.filename if file.filename 
                                                  != 'default.jpg' 
                                                  else Blog.photo
                    }
                )
            db.session.commit()
    
        else:

            new_post = Blog(
                title=title,
                body=body,
                author_id=current_user.id,
                photo=file.filename
            )
            db.session.add(new_post)
            db.session.commit()
    
        return redirect(url_for('blog.index'))

    else:
        for error in form.errors.values():
            flash(error[0])

    return render_template('blog/create.html', post=post, state=state, form=form)
        

@bp.route('/<int:user_id>/full-remove')
@login_required
def delete_all(user_id):

    if user_id == current_user.id:
 
        db.session.query(Blog).filter_by(author_id=current_user.id).delete()
        db.session.commit()
        
    else:
        
        flash('This user not authenticated', category='error')

    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id, all=False):
    post = get_post(id)

    if post.photo != 'default.jpg':
        delete_post_photo(filename=post.photo)

    db.session.delete(post)
    db.session.commit()
    
    flash('Пост удален', category='success')
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    #
    return redirect(url_for('blog.index'))

def save_post_photo(file):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    
def delete_post_photo(filename: str):
    post_filename = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    os.system(f'rm {post_filename}')