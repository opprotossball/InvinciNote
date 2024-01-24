from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import markdown

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        title = request.form.get('title')
        public = request.form.get('public') == 'on'
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id, title=title, public=public)  
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')
    #rendered_notes = [markdown.markdown(note.data) for note in current_user.notes]
    return render_template("home.html", user=current_user)

@views.route('/note/<note_id>')
@login_required
def show_note(note_id):
    note = Note.query.get(note_id)
    if note:
        if note.user_id != current_user.id:
            return "Access to note forbidden!", 403
        rendered = markdown.markdown(note.data)
        return render_template("note.html", note=note, rendered=rendered, user=current_user)
    return "Note not found", 404

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
