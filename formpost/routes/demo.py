from flask import Blueprint, render_template, current_app

demo_bp = Blueprint("demo", __name__)

@demo_bp.route("/demo/<token>")
def demo(token):
    sitekey = current_app.config.get("HCAPTCHA_SITEKEY", "")
    return render_template("demo.html", token=token, sitekey=sitekey)