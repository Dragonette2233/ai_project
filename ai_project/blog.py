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
)

from flask_login import login_required, current_user
from .validators import validate_file
from .models import User, Blog, db
from markupsafe import escape
from werkzeug.utils import secure_filename
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


@bp.route('/<int:id>/update', methods=('GET', 'POST',))
@bp.route('/create', methods=('GET', 'POST',))
@login_required
def create_update(id=None, state='create'):

    post = get_post(id)

    if request.method == 'POST':
        
        title = escape(request.form['title'])
        body = escape(request.form['body'])
        file = request.files['file']

        filename = validate_file(secure_filename(file.filename))

        if not isinstance(filename, str):

            flash(filename[0], category=filename[1])
            return render_template('blog/create.html', post=post, state=state)

        if filename != 'default.jpg':
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        if id:
            
            if file.filename != '' and post.photo != 'default.jpg':
                post_filename = os.path.join(current_app.instance_path, 'post_photos', post.photo)
                os.system(f'rm {post_filename}')
            
            if file.filename != '':

                post.photo = filename

            Blog.query.filter_by(id=id).update(
                {
                    Blog.title: title,
                    Blog.body: body,
                    Blog.photo: post.photo if file.filename != '' else Blog.photo
                }
            )

            db.session.commit()

            return redirect(url_for('blog.index'))
            
        new_post = Blog(
            title=title,
            body=body,
            author_id=current_user.id,
            photo=filename
        )
        db.session.add(new_post)
        db.session.commit()
    
        return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html', post=post, state=state)

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
        post_filename = os.path.join(current_app.instance_path, 'post_photos', post.photo)
        os.system(f'rm {post_filename}')

    db.session.delete(post)
    db.session.commit()
    
    flash('Пост удален', category='success')
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    #
    return redirect(url_for('blog.index'))