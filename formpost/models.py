import secrets
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    forms         = db.relationship("Form", backref="owner", lazy=True)

    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)


class Form(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name         = db.Column(db.String(120), nullable=False)
    token        = db.Column(db.String(32), unique=True, nullable=False,
                             default=lambda: secrets.token_urlsafe(16))
    notify_email = db.Column(db.String(120), nullable=False)
    redirect_url = db.Column(db.String(500), default="")
    enabled      = db.Column(db.Boolean, default=True)
    hcaptcha     = db.Column(db.Boolean, default=False)   # ← new
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    submissions  = db.relationship("Submission", backref="form",
                                   lazy=True, cascade="all, delete-orphan")

    @property
    def submission_count(self):
        return Submission.query.filter_by(form_id=self.id).count()


class Submission(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    form_id    = db.Column(db.Integer, db.ForeignKey("form.id"), nullable=False)
    data       = db.Column(db.JSON, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(300))
    spam       = db.Column(db.Boolean, default=False)
    read       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)