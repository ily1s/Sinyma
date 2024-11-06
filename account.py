from flask import Blueprint, render_template, redirect, session, url_for, request
from werkzeug.security import generate_password_hash
from database_query import get_user_infos, update_user_infos

account_page_bp = Blueprint("account", __name__)


@account_page_bp.route("/account")
def account():
    current_page = "account"
    if "user_id" in session:
        user_id = session["user_id"]
        user_infos = get_user_infos(user_id)
        fullname = user_infos.full_name
        return render_template(
            "account.html",
            fullname=fullname,
            user_infos=user_infos,
            current_page=current_page,
        )
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))


@account_page_bp.route("/modification", methods=["POST"])
def modification():
    new_full_name = request.form.get("fullname")
    if "user_id" in session:
        user_id = session["user_id"]
        new_full_name = request.form.get("fullname")
        new_email = request.form.get("email")
        new_password = request.form.get("mdps")

        # Check if new password is provided and not empty
        if (
            new_password and new_password.strip()
        ):  # Ensure password is not empty or whitespace
            # Hash the new password
            new_data = {
                "full_name": new_full_name,
                "email": new_email,
                "password": new_password,
                "hashed_password": generate_password_hash(new_password),
            }
        else:
            # If no new password provided, update other information without changing password
            new_data = {"full_name": new_full_name, "email": new_email}

        user_infos = get_user_infos(user_id)

        # Check if inputs differ from current user information and update if needed
        if new_full_name != user_infos.full_name:
            user_infos.full_name = new_full_name
        # Add password update logic here if required

        # Update user information in the database
        validation = update_user_infos(user_id, new_data)

        # Redirect to account page with updated information
        return redirect(url_for("account.account"))
    else:
        error = "Please log in first."
        return redirect(url_for("login.login", error=error))
