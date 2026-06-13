import requests
from threading import Thread
from flask import Blueprint, request, jsonify, redirect, current_app
from models import db, Form, Submission
from mail import send_submission_email
from limiter import limiter

submit_bp = Blueprint("submit", __name__)
HONEYPOT_FIELD = "_honey"
SKIP_FIELDS = {HONEYPOT_FIELD, "h-captcha-response", "g-recaptcha-response"}


def verify_hcaptcha(token, secret):
    try:
        r = requests.post("https://hcaptcha.com/siteverify", data={
            "secret": secret,
            "response": token,
        }, timeout=5)
        return r.json().get("success", False)
    except Exception:
        return False


@submit_bp.route("/f/<token>", methods=["POST"])
@limiter.limit("10 per minute")
def submit(token):
    f = Form.query.filter_by(token=token, enabled=True).first_or_404()

    is_spam = bool(request.form.get(HONEYPOT_FIELD, "").strip())

    if not is_spam and f.hcaptcha:
        secret   = current_app.config.get("HCAPTCHA_SECRET", "")
        hc_token = request.form.get("h-captcha-response", "")
        if not verify_hcaptcha(hc_token, secret):
            is_spam = True

    data = {k: v for k, v in request.form.items() if k not in SKIP_FIELDS}

    sub = Submission(
        form_id    = f.id,
        data       = data,
        ip_address = request.remote_addr,
        user_agent = request.user_agent.string[:300],
        spam       = is_spam,
    )
    db.session.add(sub)
    db.session.commit()

    if not is_spam:
        app = current_app._get_current_object()
        Thread(target=send_submission_email,
               args=(app, f.name, f.notify_email, sub.data, sub.ip_address)).start()

    if f.redirect_url and not is_spam:
        return redirect(f.redirect_url)

    return jsonify({"status": "spam" if is_spam else "ok", "id": sub.id}), 200