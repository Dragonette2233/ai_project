from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    g,
    session
)
import openai
from flask_login import login_required, current_user
from .models import User, Note, AiHistory, ImgHistory, db
from mtranslate import translate
from .auth_filter import check_for_cyrillic_string
import json


views = Blueprint("views", __name__)


@views.route("/", methods=("POST", "GET"))
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
            # request.form.clear()
        # return jsonify(request.form)

    return render_template("home.html")


@views.post("/delete-note")
def delete_note():
    note_data = json.loads(request.data)
    # print(request.data)
    noteID = note_data["noteID"]
    note = Note.query.get(noteID)

    if note and note.user_id == current_user.id:
        # if note.user_id = current_user.id
        db.session.delete(note)
        db.session.commit()

    return jsonify({})


@views.route("/support")
@login_required
def support():
    return render_template("support.html")


async def get_imgmodel_request(content):

    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = "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"

    if check_for_cyrillic_string(content):
        content = translate(content)

    try:

        completion = await openai.Image.acreate(
            prompt=content,
            n=3,
            size="1024x1024"
        )

        g.img_output = completion['data']
        g.img_success = True

    except Exception as ex:
        g.img_output = str(ex)
        g.img_success = False


async def get_chatmodel_request(content):

    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = "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"

    try:

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ]
        )

        # print(content)
        g.chat_output = completion.choices[0]['message']['content']
        g.chat_success = True

        # print(g.chat_output.encode('unicode_escape').decode())

    except Exception as ex:
        g.chat_output = str(ex)
        g.chat_success = False


@views.route('/assistante/delete-history/<string:model>')
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


@views.route("/assistante", methods=("GET", "POST"))
@login_required
async def assistante():

    if request.method == "POST":

        request_for_ask = request.form["ai_request"]
        if request_for_ask != "" and len(request_for_ask) > 2:
            g.chat_answer = await get_chatmodel_request(content=request_for_ask)

            ai_req_resp = AiHistory(
                ask=request.form.get("ai_request"),
                output=g.chat_output,
                output_success=g.chat_success,
                user_id=current_user.id,
            )
            db.session.add(ai_req_resp)
            db.session.commit()

        elif request_for_ask == 'se':

            # session['KEY'] = 123
            print(session)

        else:
            flash('Too short request for AI. User more than 2 characters',
                  category='error')
            # return jsonify('im here')\

        print('func is work')

    return render_template("ai_assist.html")


@views.route('/image-gen', methods=('GET', 'POST'))
async def image_gen():

    if request.method == 'POST':
        img_discription = request.form.get('img_request')

        g.img_answer = await get_imgmodel_request(content=img_discription)

        if g.img_success is False:
            flash(g.img_output)

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


@views.route('/dbg')
def dbg_route():

    history = ImgHistory.query.filter_by(
        user_id=current_user.id).order_by(ImgHistory.id.desc()).all()

    if len(history) == 0:
        print('0')

    return jsonify({})
