from flask import render_template, request, redirect, url_for, Blueprint, flash, session
from werkzeug.security import generate_password_hash
from models import User, db  # Import User model directly

# Define a Blueprint for the signup route
signup_bp = Blueprint("signup", __name__)

@signup_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please login.")
            return redirect(url_for("login.login"))

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        # Create a new user instance
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            password_hash=hashed_password,
        )

        # Add the new user to the database
        db.session.add(user)
        db.session.commit()

        # Add this line to set the user_id in the session
        session["user_id"] = user.id

        return redirect(
            url_for("login.login")
        )  # Redirect to the login page after successful signup

    return render_template("signup.html")
