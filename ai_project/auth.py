from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
)
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from .ai_forms import AuthUserForm, LoginUserForm
from .models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("auth", __name__)


@bp.route("/signin", methods=("GET", "POST"))
def sign_in():

    form = LoginUserForm()

    if request.method == "POST" and form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            flash(f"Вы вошли как {user.login}", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))

        else:
            flash("Пароль или email не совпадают.", category="error")
    else:
        for error in form.errors.values():
            flash(f"{error[0]}", category='error')

    return render_template("./auth/sign_in.html", user=current_user, form=form)


@bp.route("/signup", methods=("GET", "POST"))
def sign_up():

    form = AuthUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        login = form.login.data
        password = generate_password_hash(form.password.data)
        
        try:
            user = User(
                email=email,
                login=login,
                password=password,
            )

            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)
            flash("Success. Welcome", category="success")

            return redirect(url_for("views.home"))

        except IntegrityError:
            flash(
                "Пользователь с данными именем или email уже существует", category="error"
            )
    else:
        for error in form.errors.values():
            flash(f"{error[0]}", category='error')
            
    return render_template("./auth/sign_up.html", user=current_user, form=form)

@bp.route("/logout")
@login_required
def log_out():
    session.clear()
    logout_user()
    return redirect(url_for("auth.sign_in"))
