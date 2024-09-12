import logging
logging.basicConfig(level=logging.ERROR)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from utils.ai_generator import generate_content, classify_content
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse
from database import db
import os
import csv
from io import StringIO, BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideagenie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, IdeaSession, GeneratedIdea, IdeaRelationship, Feedback

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=request.form.get('remember_me'))
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        data = request.json
        initial_title = data.get('initial_title', '')
        initial_idea = data.get('initial_idea', '')
        feedback = data.get('feedback', [])
        session_id = data.get('session_id')
        model = data.get('model', 'gpt-4o-mini-2024-07-18')

        if session_id:
            idea_session = IdeaSession.query.get(session_id)
            if not idea_session or idea_session.user_id != current_user.id:
                return jsonify({'error': 'Invalid session ID'}), 400
        else:
            idea_session = IdeaSession(user_id=current_user.id, initial_title=initial_title, initial_idea=initial_idea)
            db.session.add(idea_session)
            db.session.commit()

        # Store feedback
        for fb in feedback:
            new_feedback = Feedback(
                session_id=idea_session.id,
                content=fb['content'],
                type=fb['type'],
                feedback=fb['feedback']
            )
            db.session.add(new_feedback)
        db.session.commit()

        # Get all feedback for the session
        all_feedback = Feedback.query.filter_by(session_id=idea_session.id).all()
        feedback_list = [{'content': fb.content, 'type': fb.type, 'feedback': fb.feedback} for fb in all_feedback]

        generated_content = generate_content(initial_title, initial_idea, feedback_list, model)
        classified_content = classify_content(generated_content, model)

        for title in classified_content['titles']:
            generated_idea = GeneratedIdea(session_id=idea_session.id, content=title['content'], category=title['category'], type='title')
            db.session.add(generated_idea)
        
        for idea in classified_content['ideas']:
            generated_idea = GeneratedIdea(session_id=idea_session.id, content=idea['content'], category=idea['category'], type='idea')
            db.session.add(generated_idea)
        
        db.session.commit()

        classified_content['session_id'] = idea_session.id
        classified_content['feedback'] = feedback_list
        return jsonify(classified_content)
    except Exception as e:
        app.logger.error(f'Error in generate route: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/mind_map/<int:session_id>')
@login_required
def get_mind_map_data(session_id):
    idea_session = IdeaSession.query.get(session_id)
    if not idea_session or idea_session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session ID'}), 400

    ideas = GeneratedIdea.query.filter_by(session_id=session_id).all()
    relationships = IdeaRelationship.query.filter_by(session_id=session_id).all()

    nodes = [{'id': idea.id, 'name': idea.content, 'type': idea.type, 'category': idea.category} for idea in ideas]
    links = [{'source': rel.idea1_id, 'target': rel.idea2_id, 'value': 1} for rel in relationships]

    return jsonify({'nodes': nodes, 'links': links})

@app.route('/add_relationship', methods=['POST'])
@login_required
def add_relationship():
    data = request.json
    idea1_id = data.get('idea1_id')
    idea2_id = data.get('idea2_id')
    session_id = data.get('session_id')

    idea_session = IdeaSession.query.get(session_id)
    if not idea_session or idea_session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session ID'}), 400

    relationship = IdeaRelationship(session_id=session_id, idea1_id=idea1_id, idea2_id=idea2_id)
    db.session.add(relationship)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/export/<int:session_id>')
@login_required
def export_session(session_id):
    idea_session = IdeaSession.query.get(session_id)
    if not idea_session or idea_session.user_id != current_user.id:
        flash('Invalid session ID')
        return redirect(url_for('index'))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'Content', 'Category'])
    
    ideas = GeneratedIdea.query.filter_by(session_id=session_id).all()
    for idea in ideas:
        writer.writerow([idea.type, idea.content, idea.category])
    
    output.seek(0)
    return send_file(BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'idea_session_{session_id}.csv')

@app.route('/my_sessions')
@login_required
def my_sessions():
    sessions = IdeaSession.query.filter_by(user_id=current_user.id).order_by(IdeaSession.created_at.desc()).all()
    return render_template('my_sessions.html', sessions=sessions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
