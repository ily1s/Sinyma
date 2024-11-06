from flask import render_template, request, redirect, url_for, Blueprint, session
from werkzeug.security import check_password_hash
from signup import User

# Define a Blueprint for the login route
login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if the password matches the hashed password
            if check_password_hash(user.password_hash, password):
                if not user.preferences:  # Check if preferences exist for the user
                    session["user_id"] = user.id
                    return redirect(
                        url_for("preferences.preferences")
                    )  # Redirect to preferences page after login if preferences do not exist
                else:
                    session["user_id"] = user.id
                    return redirect(
                        url_for("index")
                    )  # Redirect to home page after successful login if preferences exist
            else:
                error = "Invalid username or password"
                return render_template("login.html", error=error)
        else:
            error = "User not found"
            return render_template("login.html", error=error)

        
    return render_template("login.html")

