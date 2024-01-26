from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models.note import Note
from .models.encrypted_note import EncryptedNote
from .auth_validation import validate_passwords
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
        data = request.form.get('note')
        title = request.form.get('title')
        public = request.form.get('public') == 'on'
        encrypted = request.form.get('encrypted') == 'on'
        if public and encrypted:
            flash('Note cannot be public and encrypted.', category='error') 
        if not title:
            flash('Title cannot be empty.', category='error') 
        if not validate_title(title):
            flash('Title can contain up to 150 alphanumeric characters, underscores and spaces.', category='error') 
        elif not encrypted:
            new_note = Note(data=data, user_id=current_user.id, title=title, public=public)  
            db.session.add(new_note)
            db.session.commit()
            flash('Note added.', category='success')
        else:
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            validation = validate_passwords(password1, password2)
            if not validation.success:
                flash(validation.message, 'error')
            else:
                new_encrypted_note = EncryptedNote(data=data, user_id=current_user.id, title=title, password=password1)
                db.session.add(new_encrypted_note)
                db.session.commit()
                flash('Encrypted Note added.', category='success')
    return render_template("home.html", user=current_user)

@views.route('/note/<note_id>')
@login_required
def show_note(note_id):
    note = Note.query.get(note_id)
    if note:
        if (not note.public and (note.user_id != current_user.id)):
            return "Access to note forbidden!", 403
        sanitized_content = clean(note.data, tags=current_app.config['ALLOWED_TAGS'], attributes={'a': ['href']})
        rendered = markdown.markdown(sanitized_content)
        return render_template("note.html", note=note, rendered=rendered, user=current_user)
    return "Note not found", 404

@views.route('/encrypted-note/<note_id>', methods=['GET', 'POST'])
@login_required
def encrypted_note(note_id):
    note = EncryptedNote.query.get(note_id)
    if note:
        if (note.user_id != current_user.id):
            return "Access to note forbidden!", 403
        if request.method == 'POST': 
            password = request.form.get('password')
            result = note.decrypt(password)
            if result.success:
                sanitized_content = clean(result.message, tags=current_app.config['ALLOWED_TAGS'], attributes={'a': ['href']})
                rendered = markdown.markdown(sanitized_content)
                return render_template("note.html", note=note, rendered=rendered, user=current_user)
            else:
                flash('Incorrect password. Try again.', 'error')
        return render_template('encrypted_note.html', note=note, user=current_user)
    return "Note not found", 404

@views.route('/public')
@login_required
def public_notes():
    notes = (
        db.session.query(Note)
        .filter(
            Note.public == True
        )
        .order_by(Note.date.desc())
        .limit(30) 
        .all()
    )
    return render_template('public.html', notes=notes, user=current_user)

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
    pattern = r'^[a-zA-Z0-9_ąćęłńóśźżĄĆĘŁŃÓŚŹŻ ]{1,150}$'
    return re.match(pattern, title) is not None