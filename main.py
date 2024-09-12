from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from utils.ai_generator import generate_content, classify_content
from urllib.parse import urlparse
from database import db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideagenie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, IdeaSession, GeneratedIdea

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('Please use a different username.')
            return redirect(url_for('register'))
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Please use a different email address.')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=request.form.get('remember_me'))
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.json
    initial_title = data.get('initial_title', '')
    initial_idea = data.get('initial_idea', '')
    feedback = data.get('feedback', [])
    session_id = data.get('session_id')

    if session_id:
        idea_session = IdeaSession.query.get(session_id)
        if not idea_session or idea_session.user_id != current_user.id:
            return jsonify({'error': 'Invalid session ID'}), 400
    else:
        idea_session = IdeaSession(user_id=current_user.id, initial_title=initial_title, initial_idea=initial_idea)
        db.session.add(idea_session)
        db.session.commit()

    generated_content = generate_content(initial_title, initial_idea, feedback)
    classified_content = classify_content(generated_content)

    for title in classified_content['titles']:
        generated_idea = GeneratedIdea(session_id=idea_session.id, content=title['content'], category=title['category'], type='title')
        db.session.add(generated_idea)
    
    for idea in classified_content['ideas']:
        generated_idea = GeneratedIdea(session_id=idea_session.id, content=idea['content'], category=idea['category'], type='idea')
        db.session.add(generated_idea)
    
    db.session.commit()

    classified_content['session_id'] = idea_session.id
    return jsonify(classified_content)

@app.route('/my_sessions')
@login_required
def my_sessions():
    sessions = IdeaSession.query.filter_by(user_id=current_user.id).order_by(IdeaSession.created_at.desc()).all()
    return render_template('my_sessions.html', sessions=sessions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
