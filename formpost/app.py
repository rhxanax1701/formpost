import click
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from mail import mail
from limiter import limiter

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth   import auth_bp
    from routes.forms  import forms_bp
    from routes.submit import submit_bp
    from routes.demo   import demo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(forms_bp)
    app.register_blueprint(submit_bp)
    app.register_blueprint(demo_bp)

    with app.app_context():
        db.create_all()

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.password_option()
    def create_admin(email, password):
        """Seed the first admin user."""
        if User.query.filter_by(email=email).first():
            click.echo("User already exists.")
            return
        u = User(email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        click.echo(f"Admin {email} created.")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)