from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    abort,
    current_app,
    send_from_directory
)

from flask_login import login_required, current_user
from .models import User, Blog, db

from markupsafe import escape
import secrets
import os
import json
import sys


def get_post(id, check_author=True, is_all=False):
    '''post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()'''

    post = Blog.query.filter_by(id=id).first()

    #  print(post.body)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != current_user.id:
        abort(403)
    
    return post

bp = Blueprint("blog", __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    '''db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()'''

    posts = Blog.query.join(User).order_by(Blog.created.desc()).all()
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/dbg123', methods=('GET',))
def dbg123():
    
    return jsonify ({
        'static_folder': current_app.static_folder,
        'static_url': current_app.static_url_path,
    })


@bp.route('/image/<string:filename>')
def get_image(filename):
    
    post_route = os.path.join(current_app.instance_path, 'post_photos/')
    
    return send_from_directory(post_route, filename)


@bp.route('/create', '/<int:id>/update', methods=('GET', 'POST'))
@login_required
def create():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        file = request.files['file']

        if request.content_length > 2097152:

            flash('Размер фото не должен превышать 2МБ', category='error')
            return redirect(url_for('blog.create'))
        
        if file.filename == '':

            file_itself = 'json.jpg'

        elif any(['jpg' in file.filename, 'png' in file.filename, 'jpeg' in file.filename]): # NT: Security: 0
            
            filetype = file.filename.split('.')
            filename = secrets.token_urlsafe(16)
            filepath = os.path.join(current_app.instance_path, 'post_photos', f"{filename}.{filetype[1]}")
            # print(filepath)
            # fileroute = os.path.join(current_app.config["UPLOAD_ROUTE"], f"{filename}.{filetype[1]}")
            file_itself = f"{filename}.{filetype[1]}"
            # current_app.logger.info(request.content_length)
            file.save(filepath)
        
        else:
            flash('Only jpg, png, jpeg allowed', category='error')
            return redirect(url_for('blog.create'))

        if len(title) <= 5:

            flash('Title must be more than 5 characters', category='error')
        
        else:
            new_post = Blog(
                title=escape(title),
                body=escape(body),
                author_id=current_user.id,
                photo=file_itself
            )
            db.session.add(new_post)
            db.session.commit()
            # print('Done')
            # db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html', post=None, state='create')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):

    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        print(request.files)
        file = request.files['file']
        
        # photo = None
        
        if len(title) <= 5:

            flash('Title must be more than 5 characters', category='error')
        
        else:
            if file.filename != '':
               
                filetype = file.filename.split('.')
                filename = secrets.token_urlsafe(16)
                filepath = os.path.join(current_app.instance_path, 'post_photos', f"{filename}.{filetype[1]}")
                file_itself = f"{filename}.{filetype[1]}"
                file.save(filepath)
                post.photo = file_itself
            
            post = Blog.query.get(post.id)
            post.title = title
            post.body = body
            # post.photo = file_itself
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', post=post, state='update')

@bp.route('/<int:user_id>/full-remove')
@login_required
def delete_all(user_id):

    # posts = get_post(id, is_all=True)

    if user_id == current_user.id:
 
        db.session.query(Blog).filter_by(author_id=current_user.id).delete()
        db.session.commit()
        '''db = get_db()
        db.execute(
            'DELETE FROM post WHERE author_id = ?', (g.user['id'], )
        )
        db.commit()'''

    else:
        
        # <?>
        flash('This user not authenticated', category='error')

    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id, all=False):
    post = get_post(id)

    if post.photo != 'json.jpg':
        post_filename = os.path.join(current_app.instance_path, 'post_photos', post.photo)
        os.system(f'rm {post_filename}')

    db.session.delete(post)
    db.session.commit()
    
    flash('Пост удален', category='success')
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    #
    return redirect(url_for('blog.index'))