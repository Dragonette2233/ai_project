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
from .models import User, Note, AiHistory, db
import json


openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
openai.api_key = "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"
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

    return render_template("home.html", user=current_user)


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
    return render_template("support.html", user=current_user)


async def get_chatmodel_request(content):

    try:

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ]
        )

        print(content)
        g.output = completion.choices[0]['message']['content']
        g.output_success = True

        print(g.output.encode('unicode_escape').decode())

    except Exception as ex:
        g.output_success = False
        g.output = str(ex)


@views.route('/assistante/delete-history/')
@login_required
def delete_history():

    AiHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    return redirect(url_for('views.assistance'))


@views.route("/assistante", methods=("GET", "POST"))
@login_required
async def assistance():
    if request.method == "POST":

        request_for_ask = request.form["ai_request"]
        if request_for_ask != "" and len(request_for_ask) > 2:
            await get_chatmodel_request(content=request_for_ask)

            ai_req_resp = AiHistory(
                ask=request.form.get("ai_request"),
                output=g.output,
                output_success=g.output_success,
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

    return render_template("ai_assist.html", user=current_user)
