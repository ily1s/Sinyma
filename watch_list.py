from flask import render_template, Blueprint, session, request, redirect, url_for
from database_query import get_watchlist_movies, delete_row_from_watchlist
from basic_functions import get_infos_from_title
from models import User

watched_page_bp = Blueprint("watchlist", __name__)


@watched_page_bp.route("/watchlist")
def watchlist():
    user_id = None
    username = None
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if user:
            username = user.full_name
        list_infos = []

        # Retrieve the sort filter and list of selected genres
        sort_filter = request.args.get("sort-filter")
        selected_genres = request.args.getlist("genres")  # This will be a list

        if "user_id" in session:
            user_id = session["user_id"]
            watched_list = get_watchlist_movies(user_id)
            for title in watched_list:
                list_infos.append(get_infos_from_title(title))

        if sort_filter or selected_genres:
            # Apply filters only if they are provided

            if sort_filter == "top-rated":
                # Apply top-rated filter
                list_infos.sort(key=lambda x: x.get("Vote_Average", 0), reverse=True)

            elif sort_filter == "popular":
                # Apply popular filter
                list_infos.sort(key=lambda x: x.get("Popularity", 0), reverse=True)

            if selected_genres:
                # Apply genre filter
                list_infos = [
                    movie
                    for movie in list_infos
                    if any(
                        genre.lower() in (movie.get("Genres", "")).lower()
                        for genre in selected_genres
                    )
                ]

        return render_template(
            "watchlist.html",
            watchlist=list_infos,
            user_id=user_id,
            genres=get_genre_options(),
            selected_genres=selected_genres,
            sort_filter=sort_filter,
            username=username,
        )
    else:
        error = "please log in first "
        return redirect(url_for("login.login", error=error))


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


@watched_page_bp.route("/remove_from_watch_list/<title>")
def remove_from_watch_list(title):
    if "user_id" in session:
        user_id = session["user_id"]
        wish_list = get_watchlist_movies(user_id)
        # Remove the movie with the given title from the liked list if it exists
        if title in wish_list:
            delete_row_from_watchlist(user_id, title)
        return redirect(url_for("watchlist.watchlist"))