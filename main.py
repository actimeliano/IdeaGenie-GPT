import logging
logging.basicConfig(level=logging.ERROR)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from utils.ai_generator import generate_content, classify_content
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

from models import User, IdeaSession, GeneratedIdea

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

# ... (keep all other routes unchanged)

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

        generated_content = generate_content(initial_title, initial_idea, feedback, model)
        classified_content = classify_content(generated_content, model)

        for title in classified_content['titles']:
            generated_idea = GeneratedIdea(session_id=idea_session.id, content=title['content'], category=title['category'], type='title')
            db.session.add(generated_idea)
        
        for idea in classified_content['ideas']:
            generated_idea = GeneratedIdea(session_id=idea_session.id, content=idea['content'], category=idea['category'], type='idea')
            db.session.add(generated_idea)
        
        db.session.commit()

        classified_content['session_id'] = idea_session.id
        return jsonify(classified_content)
    except Exception as e:
        app.logger.error(f'Error in generate route: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

# ... (keep all other routes unchanged)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
