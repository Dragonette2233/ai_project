from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g, session
)
from flask_login import login_user, login_required, logout_user, current_user
from ai_project.auth_filter import UserInfo, check_for_cyrillic
from ai_project.auth_filter import get_flash_message_for_cyrillic
from sqlalchemy.exc import IntegrityError
from .models import User, db

from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/')
def auth_home():
    
    return {
        'Cookies': session,
        'AuthStatus': current_user.is_authenticated
    }

@auth.route('/signin', methods=('GET', 'POST'))
def sign_in():

    if request.method == 'POST':

        email= request.form.get('email')
        password = request.form.get('pass_main')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            flash('You are logged in', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
            
        
        else:
            flash('Incorrect email or password.', category='error')


    return render_template ('./auth/sign_in.html', user=current_user)
        
@auth.route('/signup', methods=('GET', 'POST'))
def sign_up():

    if request.method == 'POST':

        userinfo = UserInfo(**request.form)
        cyrillic_check = check_for_cyrillic(userinfo)
        
        if cyrillic_check is not False:
            
            flash(get_flash_message_for_cyrillic(cyrillic_check), category='error')
            
        elif len(userinfo.pass_main) < 8:

            flash('Password should be more than 8 chars.', category='error')
        
        elif userinfo.pass_main != userinfo.pass_confirm:
            
            flash('Passwords dont match.', category='error')
            
        else:
            # print(user)
            try:

                user = User(
                    login=userinfo.login,
                    email=userinfo.email,
                    password=generate_password_hash(userinfo.pass_confirm)
                )

                db.session.add(user)
                db.session.commit()

                # session['user_id'] = 
                login_user(user, remember=True)
                flash('Success. Welcome', category='success')

                redirect(url_for('views.home'))

            except IntegrityError:

                flash('User with this username of email already exists.', category='error')

            # return redirect(url_for('hello'))
    
    return render_template('./auth/sign_up.html', user=current_user)

@auth.route('/logout')
@login_required
def log_out():
    # session.clear()
    logout_user()
    return redirect(url_for('auth.sign_in'))

'''@auth.before_app_request 
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()'''