from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import numpy as np
from Scraping import update_articles
from movie_news import movie_news_bp
from movie_page import movie_page_bp
from watch_list import watched_page_bp
from liked_list import liked_page_bp
from wish_list import wishlist_page_bp
from signup import signup_bp
from login import login_bp
from preferences import preferences_bp
from more_movies import more_movies_bp
from searched_movies import searched_movies_bp
from models import db, MovieRating, User, likedlist
from Mov_content_based_model import get_recommendations
from cf import collaborative_filtering, neural_network_collaborative_filtering
from account import account_page_bp
from historique import history_page_bp
from basic_functions import get_popular_movies, get_top_rated_movies
from database_query import (
    get_visited_movies,
    get_saved_movies,
    get_liked_movies,
    get_watchlist_movies,
    get_fav_movies_preference,
    add_comment,
    rate_movie,
)
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "azerty123"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:SqlRoot0000@localhost/RECPROJ"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy object
db.init_app(app)

# Register blueprints
app.register_blueprint(movie_news_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(movie_page_bp)
app.register_blueprint(more_movies_bp)
app.register_blueprint(watched_page_bp)
app.register_blueprint(liked_page_bp)
app.register_blueprint(wishlist_page_bp)
app.register_blueprint(searched_movies_bp)
app.register_blueprint(account_page_bp)
app.register_blueprint(history_page_bp)


# Schedule the update_articles function to run every day at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_articles, trigger="cron", hour=0)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.before_request
def before_request():
    # Check if the user is not logged in and the session variable 'user_id' exists
    if "user_id" in session and not User.query.get(session["user_id"]):
        # Clear the session variable 'user_id'
        session.pop("user_id", None)


def generate_user_item_matrix():
    # Fetch all movie ratings from the database
    movie_ratings = MovieRating.query.all()

    # Get unique user IDs and movie IDs
    user_ids = set()
    movie_ids = set()
    ratings_dict = {}  # Dictionary to store ratings for each (user, movie) pair
    for rating in movie_ratings:
        user_ids.add(rating.user_id)
        movie_ids.add(rating.movie_id)
        # Store the rating in the ratings dictionary using (user_id, movie_id) as the key
        ratings_dict[(rating.user_id, rating.movie_id)] = rating.rating

    # Map movie IDs to column indices
    movie_id_to_index = {movie_id: i for i, movie_id in enumerate(movie_ids)}

    # Initialize user-item matrix with zeros
    user_item_matrix = np.zeros((len(user_ids), len(movie_ids)))

    # Fill user-item matrix with ratings
    for user_index, user_id in enumerate(sorted(user_ids)):
        for movie_id in movie_ids:
            movie_index = movie_id_to_index[movie_id]
            # If the rating for the current (user, movie) pair exists, assign it to the matrix
            if (user_id, movie_id) in ratings_dict:
                user_item_matrix[user_index, movie_index] = ratings_dict[
                    (user_id, movie_id)
                ]

    return user_item_matrix, list(movie_ids)


@app.route("/add_comment", methods=["POST"])
def add_comment_route():
    return add_comment()


@app.route("/rate_movie", methods=["POST"])
def rate_movie_route():
    return rate_movie()


@app.route("/movie/like_count/<int:movie_id>")
def get_like_count(movie_id):
    like_count = likedlist.query.filter_by(movie_id=movie_id).count()
    return jsonify({"like_count": like_count})


# In your logout route
@app.route("/logout")
def logout():
    # Clear the session
    session.pop("user_id", None)
    return redirect(url_for("index"))  # Redirect to home page after logout


@app.route("/", methods=["GET", "POST"])
def index():
    recommended_movies = []
    collaborative_filtering_recommendations = []
    neural_network_recommendations = []
    username = None
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
        visited_movies = get_visited_movies(user_id)
        watched_list = get_watchlist_movies(user_id)
        liked_movies = get_liked_movies(user_id)
        wish_list = get_saved_movies(user_id)
        favorite_movies_pref = get_fav_movies_preference(user_id)
        recommended_movies = get_recommendations(
            favorite_movies_pref,
            visited_movies,
            watched_list,
            liked_movies,
            wish_list,
            columns=["Title", "Genres", "Director", "Poster_Path", "Tagline"],
        )

        # Generate user-item matrix and movie titles
        user_item_matrix, movie_titles = generate_user_item_matrix()

        # Get collaborative filtering recommendations
        collaborative_filtering_recommendations = collaborative_filtering(
            user_id, user_item_matrix, movie_titles, num_recommendations=10
        )
        if collaborative_filtering_recommendations is None:
            collaborative_filtering_recommendations = []
        # Get neural network recommendations
        neural_network_recommendations = neural_network_collaborative_filtering(
            user_id, user_item_matrix, movie_titles, num_recommendations=10
        )
        print("neural : ", neural_network_recommendations)
        if neural_network_recommendations is None:
            neural_network_recommendations = []

    df_populaire = get_popular_movies()
    df_top_rated = get_top_rated_movies()

    populaire_mov = df_populaire.iloc[0:30].to_dict(orient="records")
    top_movies = df_top_rated.iloc[0:30].to_dict(orient="records")
    return render_template(
        "index.html",
        collaborative_filtering_recommendations=collaborative_filtering_recommendations,
        neural_network_recommendations=neural_network_recommendations,
        recommended_movies=recommended_movies,
        top_rated_movies=top_movies,
        popular_movies=populaire_mov,
        fan_favorites=top_movies,
        username=username,
    )


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()  # Drop existing tables
        db.create_all()  # Create tables with updated schema
    app.run(debug=True)
