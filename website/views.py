from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import markdown
from bleach import clean
import re

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        title = request.form.get('title')
        public = request.form.get('public') == 'on'
        if not title:
            flash('Add title!', category='error') 
        if not validate_title(title):
            flash('Title can contain only alphanumeric characters and underscores.', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id, title=title, public=public)  
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user=current_user)

@views.route('/note/<note_id>')
@login_required
def show_note(note_id):
    note = Note.query.get(note_id)
    if note:
        if note.user_id != current_user.id:
            return "Access to note forbidden!", 403
        sanitized_content = clean(note.data, tags=current_app.config['ALLOWED_TAGS'], attributes={'a': ['href']})
        rendered = markdown.markdown(sanitized_content)
        return render_template("note.html", note=note, rendered=rendered, user=current_user)
    return "Note not found", 404

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

def validate_title(title):
    pattern = r'^[a-zA-Z0-9_]{1,16}$'
    return re.match(pattern, title) is not None