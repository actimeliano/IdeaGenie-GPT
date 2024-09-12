from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class IdeaSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    initial_title = db.Column(db.String(200))
    initial_idea = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('idea_sessions', lazy=True))

class GeneratedIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'title' or 'idea'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    session = db.relationship('IdeaSession', backref=db.backref('generated_ideas', lazy=True))

class IdeaRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('idea_session.id'), nullable=False)
    idea1_id = db.Column(db.Integer, db.ForeignKey('generated_idea.id'), nullable=False)
    idea2_id = db.Column(db.Integer, db.ForeignKey('generated_idea.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    session = db.relationship('IdeaSession', backref=db.backref('idea_relationships', lazy=True))
    idea1 = db.relationship('GeneratedIdea', foreign_keys=[idea1_id])
    idea2 = db.relationship('GeneratedIdea', foreign_keys=[idea2_id])
