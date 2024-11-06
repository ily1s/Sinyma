from flask import render_template, request, Blueprint, session
import pandas as pd
from models import User

# Define a Blueprint for the more_movies route
more_movies_bp = Blueprint("more_movies", __name__)


@more_movies_bp.route("/more_movies")
def more_movies():
    user_id = None
    username = None
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
    # Load movie dataset
    movie_data = pd.read_csv("movie_data.csv")


    # Filter movies based on user selection
    filters = request.args.getlist("filter")
    sort_filter = request.args.get("sort-filter")
    genre_filters = request.args.getlist("genres")

    filtered_movies = (
        movie_data.copy()
    )  # Make a copy to avoid modifying the original DataFrame

    if sort_filter == "top-rated":
        # Apply top-rated filter
        mean_vote = filtered_movies["Vote_Average"].mean()
        filtered_movies = filtered_movies[
            (filtered_movies["Vote_Average"] > mean_vote)
            & (filtered_movies["Vote_Count"] >= 1000)
        ].sort_values(["Vote_Average"], ascending=False)
        filtered_movies = filtered_movies[:100]

    elif sort_filter == "popular":
        # Apply popular filter
        filtered_movies = filtered_movies.sort_values(["Popularity"], ascending=False)
        filtered_movies = filtered_movies[:100]

    if genre_filters:
        # Fill NaN values in the "Genres" column with an empty string
        filtered_movies["Genres"] = filtered_movies["Genres"].fillna("")
        
        # Create a boolean series that is True for rows where "Genres" contains any of the selected genres
        genre_match = filtered_movies["Genres"].apply(
            lambda genres: any(genre in genres for genre in genre_filters)
        )
        # Filter the movies by the boolean series
        filtered_movies = filtered_movies[genre_match]

    # Pagination
    page = request.args.get("page", 1, type=int)
    movies_per_page = 20
    total_movies = filtered_movies.shape[0]
    total_pages = (total_movies + movies_per_page - 1) // movies_per_page
    movies_to_display = filtered_movies.iloc[
        (page - 1) * movies_per_page : page * movies_per_page
    ]

    # Pass filtered movie data, pagination information, and current page number to the template
    return render_template(
        "more_movies.html",
        movies=movies_to_display.to_dict("records"),
        total_pages=total_pages,
        current_page=page,  # Pass the current page number to the template
        sort_filter=sort_filter,
        genres=get_genre_options(),
        selected_genres=genre_filters,  # Pass genre filter options to the template
        username=username,
    )


def get_genre_options():
    genres = [
        "Action",
        "Science Fiction",
        "Adventure",
        "Drama",
        "Crime",
        "Thriller",
        "Fantasy",
        "Comedy",
        "Romance",
        "Western",
        "Mystery",
        "War",
        "Animation",
        "Family",
        "Horror",
        "History",
        "Music",
        "TV Movie",
        "Documentary",
    ]
    return genres

