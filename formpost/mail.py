from flask_mail import Mail, Message

mail = Mail()

def send_submission_email(app, form_name, notify_email, data, ip):
    subject = f"[FormPost] New submission: {form_name}"
    rows = "\n".join(f"  {k}: {v}" for k, v in data.items())
    body = f"New submission for '{form_name}':\n\n{rows}\n\nIP: {ip}"

    with app.app_context():
        sender = app.config.get("MAIL_USERNAME") or app.config.get("MAIL_DEFAULT_SENDER")
        msg = Message(subject, recipients=[notify_email], sender=sender, body=body)
        mail.send(msg)