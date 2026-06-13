import csv
import io
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Form, Submission
from flask import Response

forms_bp = Blueprint("forms", __name__)

@forms_bp.route("/dashboard")
@login_required
def dashboard():
    forms = Form.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", forms=forms)

@forms_bp.route("/forms/new", methods=["GET", "POST"])
@login_required
def new_form():
    if request.method == "POST":
        name         = request.form.get("name", "").strip()
        notify_email = request.form.get("notify_email", "").strip()
        redirect_url = request.form.get("redirect_url", "").strip()
        hcaptcha     = bool(request.form.get("hcaptcha"))
        if not name or not notify_email:
            flash("Name and notification email are required.", "error")
            return render_template("new_form.html")
        f = Form(user_id=current_user.id, name=name, notify_email=notify_email,
                 redirect_url=redirect_url, hcaptcha=hcaptcha)
        db.session.add(f)
        db.session.commit()
        flash(f"Form created! Endpoint: /f/{f.token}", "success")
        return redirect(url_for("forms.dashboard"))
    return render_template("new_form.html")

@forms_bp.route("/forms/<int:form_id>")
@login_required
def view_form(form_id):
    f = Form.query.filter_by(id=form_id, user_id=current_user.id).first_or_404()
    subs = Submission.query.filter_by(form_id=f.id, spam=False)\
                           .order_by(Submission.created_at.desc()).all()
    return render_template("view_form.html", form=f, submissions=subs)

@forms_bp.route("/forms/<int:form_id>/delete", methods=["POST"])
@login_required
def delete_form(form_id):
    f = Form.query.filter_by(id=form_id, user_id=current_user.id).first_or_404()
    db.session.delete(f)
    db.session.commit()
    flash("Form deleted.", "success")
    return redirect(url_for("forms.dashboard"))


@forms_bp.route("/forms/<int:form_id>/export")
@login_required
def export_csv(form_id):
    f = Form.query.filter_by(id=form_id, user_id=current_user.id).first_or_404()
    subs = Submission.query.filter_by(form_id=f.id, spam=False).all()

    if not subs:
        flash("No submissions to export.", "error")
        return redirect(url_for("forms.view_form", form_id=form_id))

    # Get all unique keys across submissions
    keys = list({k for s in subs for k in s.data.keys()})

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "date", "ip"] + keys)
    writer.writeheader()
    for s in subs:
        row = {"id": s.id, "date": s.created_at, "ip": s.ip_address}
        row.update(s.data)
        writer.writerow(row)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={f.name}_submissions.csv"}
    )