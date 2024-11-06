from flask import render_template, Blueprint, session, redirect, url_for
from database_query import get_visited_movies
from basic_functions import get_infos_from_title, get_article_infos_from_title
from models import User, UserInteraction
import json

history_page_bp = Blueprint("history", __name__)


@history_page_bp.route("/history")
def movies_history():
    current_page = "historique"
    user_id = None
    username = None
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
        Visited_list_infos = []
        visited_movies = get_visited_movies(user_id)
        for title in visited_movies:
            Visited_list_infos.append(get_infos_from_title(title))

        return render_template(
            "history.html",
            Visited_movies=Visited_list_infos[:20],
            user_id=user_id,
            username=username,
            current_page=current_page,
        )
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))


@history_page_bp.route("/history/articles")
def articles_history():
    current_page = "articles_history"
    user_id = None
    username = None
    read_articles = []
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).first()
        if user_interactions:
            user_read_articles = json.loads(user_interactions.read_articles)
        else:
            user_read_articles = []
        for article in user_read_articles:
            read_articles.append(get_article_infos_from_title(article))
        read_articles = read_articles[-20:][::-1]
        return render_template(
            "articles_history.html",
            read_articles=read_articles,
            user_id=user_id,
            username=username,
            current_page=current_page,
        )
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))
