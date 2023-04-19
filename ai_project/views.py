from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from .models import User, Note, db
import json


views = Blueprint('views', __name__)

@views.route('/', methods=('POST', 'GET'))
@login_required
def home():

    if request.method == 'POST':
        
        note = request.form.get('note')

        if len(note) <= 3:

            flash('Note is too short. Use more than 3 characters', category='error')
        
        else:

            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            # request.form.clear()
        # return jsonify(request.form)

    return render_template('home.html', user=current_user)

@views.post('/delete-note')
def delete_note():

    note_data = json.loads(request.data)
    # print(request.data)
    noteID = note_data['noteID']
    note = Note.query.get(noteID)

    if note and note.user_id == current_user.id:
        # if note.user_id = current_user.id
        db.session.delete(note)
        db.session.commit()

    return jsonify({})


@views.route('/support')
@login_required
def support():
    return render_template('support.html', user=current_user)

@views.route('/assistante', methods=('GET', 'POST'))
@login_required
def assistance():

    
    # user = User.query.filter_by(email=email).first()
    return render_template('ai_assist.html', user=current_user)