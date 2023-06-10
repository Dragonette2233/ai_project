import markupsafe
import json
from .openai_cstmapi import (
    get_imgmodel_request,
    get_chatmodel_request
)
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    g,
)

from flask_login import login_required, current_user
from .models import User, Note, AiHistory, ImgHistory, db
from .key_cryptograpy import generete_cipher

bp = Blueprint("views", __name__)

@bp.route("/", methods=("POST", "GET"))
@login_required
def home():

    if request.method == "POST":
        note = request.form.get("note")

        if len(note) <= 3:
            flash("Note is too short. Use more than 3 characters", category="error")

        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
           
    return render_template("home.html")


@bp.post("/delete-note")
def delete_note():
    note_data = json.loads(request.data)

    noteID = note_data["noteID"]
    note = Note.query.get(noteID)

    if note and note.user_id == current_user.id:
        # if note.user_id = current_user.id
        db.session.delete(note)
        db.session.commit()

    return jsonify({})

@bp.route('/faq', methods=["GET", "POST"])
def faq():

    if request.method == "GET":
        return render_template("faq.html")


    with open(f'logs/feedback_from_{current_user.login}', 'a+') as feedfile:

        feed_message=f'''Тип:{request.form.get('category')}\nСообщение:{request.form.get('body')}\n\n'''
        feedfile.write(feed_message)
    
    flash('Сообщение отправлено.', category='success')
    
    return redirect(url_for('views.faq'))


@bp.route('/assistante/delete-history/<string:model>')
@login_required
def delete_history(model):

    match model:
        case 'assistante':
            AiHistory.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
        case 'image_gen':
            ImgHistory.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()  
        case _:
            pass

    flash('История очищена')
    return redirect(url_for(f'views.{model}'))


@bp.route("/assistante", methods=("GET", "POST"))
@login_required
async def assistante():

    if request.method == "POST":
        
        request_for_ask = request.form["ai_request"]
        
        """
            Response message and success stored in "g" object 
        """
        await get_chatmodel_request(content=request_for_ask)

        ai_req_resp = AiHistory(
            ask=markupsafe.escape(request_for_ask),
            output=markupsafe.escape(g.chat_output),
            output_success=g.chat_success,
            user_id=current_user.id,
        )
        db.session.add(ai_req_resp)
        db.session.commit()
        return redirect(url_for('views.assistante'))
            
    return render_template("ai_assist.html")


@bp.route('/image-gen', methods=('GET', 'POST'))
async def image_gen():

    if request.method == 'POST':
        img_discription = request.form.get('img_request')

        g.img_answer = await get_imgmodel_request(content=img_discription)

        if g.img_success is False:
            flash(g.img_output, category='error')

        else:

            img_req_resp = ImgHistory(
                url_1=g.img_output[0]['url'],
                url_2=g.img_output[1]['url'],
                url_3=g.img_output[2]['url'],
                user_id=current_user.id
            )

            db.session.add(img_req_resp)
            db.session.commit()

        return redirect(url_for('views.image_gen'))

    history = ImgHistory.query.filter_by(
        user_id=current_user.id).order_by(ImgHistory.id.desc()).all()

    return render_template('image_gen.html', history=history)


@bp.route('/dbg')
def dbg_route():

    history = ImgHistory.query.filter_by(
        user_id=current_user.id).order_by(ImgHistory.id.desc()).all()

    if len(history) == 0:
        print('0')

    return jsonify({})

@bp.route('/account-settings', methods=('GET', 'POST'))
def account():

    if request.method == 'POST':
        api_key = request.form.get('apik')
        if len(api_key) > 20:
            
            api_key = generete_cipher(api_key)

            User.query.filter_by(id=current_user.id).update(
                {
                    User.openai_api: api_key
                }
            )
            db.session.commit()
            flash('API ключ обновлен')
            
        else:
            flash('API ключ слишком короткий')

        new_password = request.form.get('new_password')

        if new_password != '':
            ...

    return render_template('settings.html')