import os
import json
import urllib.request
import urllib.error
import html

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or "local-development-secret-change-before-deployment"
)
database_url = os.environ.get("DATABASE_URL", "sqlite:///bookings.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(160))
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    preferred_date = db.Column(db.String(20))
    preferred_time = db.Column(db.String(30))
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="New", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    return render_template("index.html")

def send_booking_email(booking):
    api_key = os.environ.get("RESEND_API_KEY")
    recipient = os.environ.get("BOOKING_NOTIFICATION_EMAIL")
    sender = os.environ.get("RESEND_FROM_EMAIL")

    print("EMAIL FUNCTION CALLED")
    print("API KEY LOADED:", bool(api_key))
    print("RECIPIENT LOADED:", bool(recipient))
    print("SENDER LOADED:", bool(sender))

    if not api_key or not recipient or not sender:
        print("Email settings are missing.")
        return False

    details = html.escape(booking.details)

    email_data = {
        "from": sender,
        "to": [recipient],
        "subject": f"New portfolio booking from {booking.full_name}",
        "html": f"""
            <h2>New Booking Request</h2>
            <p><strong>Name:</strong> {html.escape(booking.full_name)}</p>
            <p><strong>Company:</strong> {html.escape(booking.company or "Not provided")}</p>
            <p><strong>Email:</strong> {html.escape(booking.email)}</p>
            <p><strong>Phone:</strong> {html.escape(booking.phone)}</p>
            <p><strong>Service:</strong> {html.escape(booking.service)}</p>
            <p><strong>Date:</strong> {html.escape(booking.preferred_date or "Not specified")}</p>
            <p><strong>Time:</strong> {html.escape(booking.preferred_time or "Not specified")}</p>
            <p><strong>Details:</strong> {details}</p>
        """
    }

    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(email_data).encode("utf-8"),
       headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "GanzaIvanPortfolio/1.0"
},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print("Booking email sent:", response.status)
            return True

    except urllib.error.HTTPError as error:
        print("Email service error:", error.code)
        print(error.read().decode("utf-8", errors="replace"))
        return False

    except Exception as error:
        print("Email notification failed:", error)
        return False



@app.route("/book", methods=["POST"])
def book():
    required = ["full_name", "email", "phone", "service", "details"]

    if any(not request.form.get(field, "").strip() for field in required):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("home") + "#booking")

    booking = Booking(
        full_name=request.form["full_name"].strip(),
        company=request.form.get("company", "").strip(),
        email=request.form["email"].strip(),
        phone=request.form["phone"].strip(),
        service=request.form["service"].strip(),
        preferred_date=request.form.get("preferred_date", "").strip(),
        preferred_time=request.form.get("preferred_time", "").strip(),
        details=request.form["details"].strip()
    )

    db.session.add(booking)
    db.session.commit()

    email_sent = send_booking_email(booking)

    if email_sent:
        print("Booking saved and email notification sent.")
    else:
        print("Booking saved, but email notification was not sent.")

    flash(
        "Your booking request has been received. I'll contact you soon.",
        "success"
    )

    return redirect(url_for("home") + "#booking")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = os.environ.get("ADMIN_PASSWORD")
        password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
        submitted = request.form.get("password", "")
        valid = bool(password and submitted == password)
        if password_hash:
            valid = check_password_hash(password_hash, submitted)
        if valid:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Incorrect admin password.", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin.html", bookings=bookings)

@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def update_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get("status", "New")
    if status in {"New", "Contacted", "In progress", "Completed", "Declined"}:
        booking.status = status
        db.session.commit()
    return redirect(url_for("admin"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
