from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    g,
    session,
    abort,
    current_app
)

from flask_login import login_required, current_user
from .models import User, Note, AiHistory, ImgHistory, Blog, db
from mtranslate import translate
from .auth_filter import check_for_cyrillic_string
from markupsafe import escape
import secrets
import os
import json
import sys


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
    # print(posts[0].author.login)
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/dbg123', methods=('GET',))
def dbg123():
    print(current_app.config["UPLOAD_FOLDER"])
    print(current_app.static_folder)
    print(current_app)
    return jsonify ({})

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print(request.form)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        file = request.files['file']

        if any(['jpg' in file.filename, 'png' in file.filename, 'jpeg' in file.filename]): # NT: Security: 0
            
            filetype = file.filename.split('.')
            filename = secrets.token_urlsafe(16)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{filename}.{filetype[1]}")
            fileroute = os.path.join(current_app.config["UPLOAD_ROUTE"], f"{filename}.{filetype[1]}")
            file.save(filepath)
        
        elif file.filename == '':

            fileroute = None
        else:
            flash('Only jpg, png, jpeg allowed', category='error')
            return redirect(url_for('blog.create'))

        if len(title) <= 5:

            flash('Title must be more than 5 characters')
        
        else:
            new_post = Blog(
                title=escape(title),
                body=escape(body),
                author_id=current_user.id,
                photo=fileroute
            )
            db.session.add(new_post)
            db.session.commit()
            print('Done')
            # db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    '''post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()'''

    post = Blog.query.filter_by(id=id).first()

    print(post.body)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != current_user.id:
        abort(403)
    
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):

    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        # photo = None
        
        if len(title) <= 5:

            flash('Title must be more than 5 characters')
        
        else:
            post = Blog.query.get(post.id)
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/full-remove')
@login_required
def delete_all(id):

    if id == current_user.id:

        db = get_db()
        db.execute(
            'DELETE FROM post WHERE author_id = ?', (g.user['id'], )
        )
        db.commit()

    else:

        flash('This user not authenticated')

    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id, all=False):
    post = get_post(id)

    if post.photo is not None:
        post_filename = post.photo.split('/static/post_photos/')[1]
        os.system(f'rm {current_app.config["UPLOAD_FOLDER"]}/{post_filename}')

    db.session.delete(post)
    db.session.commit()
    
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    #
    return redirect(url_for('blog.index'))