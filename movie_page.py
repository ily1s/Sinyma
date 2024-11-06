from flask import render_template, redirect, Blueprint, url_for, request, session
from Mov_content_based_model import get_recommendations
from basic_functions import df, get_list_cast
from login import login_bp
from database_query import (
    add_row_to_visitedlist,
    add_row_to_likedlist,
    add_row_to_wishlist,
    add_row_to_watchlist,
    get_visited_movies,
    get_saved_movies,
    get_liked_movies,
    get_watchlist_movies,
    get_user_rating,
    get_user_comment,
)
from models import User
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Define a Blueprint for the movie_news route
movie_page_bp = Blueprint("movie", __name__)
movie_page_bp.register_blueprint(login_bp)


@movie_page_bp.route("/movie/<title>", methods=["GET", "POST"])
def movie_details(title):
    similar_movies = []
    user_id = None
    username = None
    user_rating = None
    watched = False
    saved = False
    liked = False

    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
        watched = title in get_watchlist_movies(user_id)
        saved = title in get_saved_movies(user_id)
        liked = title in get_liked_movies(user_id)

        if not title in get_visited_movies(user_id):
            add_row_to_visitedlist(user_id, title)

        # Get user's rating for the movie
        user_rating = get_user_rating(
            user_id, title
        )  # Define a function to fetch user's rating

    similar_movies = get_recommendations(
        [],
        [title],
        [],
        [],
        [],
        columns=["Title", "Genres", "Director", "Poster_Path", "Tagline"],
    )

    movie_details = df[df["Title"] == title].iloc[0]  # Assuming 'Title' is unique
    movie_cast = get_list_cast(movie_details["Title"])

    # Fetch all comments for the movie
    comments = get_user_comment(title)

    # Initialize VADER sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Perform sentiment analysis on comments and filter positive comments
    positive_comments = []
    for comment in comments:
        scores = sid.polarity_scores(comment.comment_text)
        if scores["compound"] >= 0.05:
            positive_comments.append(comment)

    # Define the movie object
    movie = {
        "Title": title,
        "watched": watched,  
        "saved": saved,
        "liked": liked,
    }

    return render_template(
        "movie.html",
        moviee = movie,
        movie=movie_details,
        movie_cast=movie_cast,
        similar_movies=similar_movies,
        user_id=user_id,
        user_rating=user_rating,
        username=username,
        comments=comments,
        positive_comments=positive_comments,
        watched=watched,  # Pass the watched variable to the template
    )


@movie_page_bp.route("/add_to_liked_list/", methods=["POST"])
def add_to_liked_list():
    title = request.form.get("title")
    if "user_id" in session:
        user_id = session["user_id"]
        if not title in get_liked_movies(user_id):
            add_row_to_likedlist(user_id, title)
        return redirect(url_for("movie.movie_details", title=title))

    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))


@movie_page_bp.route("/add_to_watched_list/", methods=["POST"])
def add_to_watched_list():
    if "user_id" in session:
        user_id = session["user_id"]
        title = request.form.get("title")  # Get movie title from form data
        if not title in get_watchlist_movies(user_id):
            add_row_to_watchlist(user_id, title)

        return redirect(url_for("movie.movie_details", title=title))
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))


@movie_page_bp.route("/add_to_wish_list/", methods=["POST"])
def add_to_wish_list():
    if "user_id" in session:
        user_id = session["user_id"]
        title = request.form.get("title")  # Get movie title from form data
        if not title in get_saved_movies(user_id):
            add_row_to_wishlist(user_id, title)
        return redirect(url_for("movie.movie_details", title=title))
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))
