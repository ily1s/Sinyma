from flask import render_template, Blueprint, request, session
from basic_functions import search_movies_from_text
from models import User


searched_movies_bp = Blueprint("search", __name__)


@searched_movies_bp.route("/searched_movies", methods=["POST"])
def searched_movies():
    username = None
    user_id = "Guest"
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        username = user.full_name
    input_text = request.form["search"]
    searched_movies = search_movies_from_text(input_text)

    if len(searched_movies):
        return render_template(
            "searched_movies.html",
            searched_movies=searched_movies,
            user_id=user_id,
            search=input_text,
            username=username,
        )
    else:
        error = "Sorry , movie not found 😢"
        return render_template(
            "searched_movies.html",
            error=error,
            user_id=user_id,
            search=input_text,
            username=username,
        )
