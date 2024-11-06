from flask import request, session, url_for, redirect
from basic_functions import get_id_from_title
from models import (
    db,
    User,
    visitedlist,
    Watchlist,
    likedlist,
    wishlist,
    Comment,
    MovieRating,
    Preference
)
from sqlalchemy import desc


def add_row_to_watchlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    watchlist_entry = Watchlist(movie_id=movie_id, user_id=user_id, watch_mov=movie)
    db.session.add(watchlist_entry)

    db.session.commit()


def add_row_to_likedlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    likedlist_entry = likedlist(movie_id=movie_id, user_id=user_id, liked_mov=movie)
    db.session.add(likedlist_entry)

    db.session.commit()


def add_row_to_wishlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    wishlist_entry = wishlist(movie_id=movie_id, user_id=user_id, wish_mov=movie)
    db.session.add(wishlist_entry)

    db.session.commit()


def add_row_to_visitedlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    visitedlist_entry = visitedlist(
        movie_id=movie_id, user_id=user_id, visited_mov=movie
    )
    db.session.add(visitedlist_entry)

    db.session.commit()


def get_visited_movies(user_id):
    # Query to fetch movies from Watchlist table based on user_id
    visited_movies = (
        visitedlist.query.filter_by(user_id=user_id)
        .order_by(desc(visitedlist.id))
        .all()
    )
    return [
        movie.visited_mov for movie in visited_movies
    ]  # Extract movie titles into a list


def get_watchlist_movies(user_id):
    # Query to fetch movies from Watchlist table based on user_id
    watchlist_movies = (
        Watchlist.query.filter_by(user_id=user_id).order_by(desc(Watchlist.id)).all()
    )
    return [
        movie.watch_mov for movie in watchlist_movies
    ]  # Extract movie titles into a list


def get_liked_movies(user_id):
    # Query to fetch movies from Watchlist table based on user_id
    visited_movies = (
        likedlist.query.filter_by(user_id=user_id).order_by(desc(likedlist.id)).all()
    )
    return [
        movie.liked_mov for movie in visited_movies
    ]  # Extract movie titles into a list


def get_saved_movies(user_id):
    # Query to fetch movies from Watchlist table based on user_id
    saved_movies = (
        wishlist.query.filter_by(user_id=user_id).order_by(desc(wishlist.id)).all()
    )
    return [
        movie.wish_mov for movie in saved_movies
    ]  # Extract movie titles into a list


def get_fav_movies_preference(user_id):
    # Query to fetch movies from Watchlist table based on user_id
    fav_movies = Preference.query.filter_by(user_id=user_id).first()
    if fav_movies:
        fav_list = [
            fav_movies.favorite_movie1,
            fav_movies.favorite_movie2,
            fav_movies.favorite_movie3,
        ]
    else:
        fav_list = []
    return fav_list


def delete_row_from_likedlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    # Find the entry to delete based on user_id and movie_id
    entry_to_delete = likedlist.query.filter_by(
        user_id=user_id, movie_id=movie_id
    ).first()

    if entry_to_delete:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return True  # Indicate successful deletion
    else:
        return False  # Entry not found or deletion failed


def delete_row_from_watchlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    # Find the entry to delete based on user_id and movie_id
    entry_to_delete = Watchlist.query.filter_by(
        user_id=user_id, movie_id=movie_id
    ).first()

    if entry_to_delete:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return True  # Indicate successful deletion
    else:
        return False  # Entry not found or deletion failed


def delete_row_from_wishlist(user_id, movie):
    movie_id = get_id_from_title(movie)
    # Find the entry to delete based on user_id and movie_id
    entry_to_delete = wishlist.query.filter_by(
        user_id=user_id, movie_id=movie_id
    ).first()

    if entry_to_delete:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return True  # Indicate successful deletion
    else:
        return False  # Entry not found or deletion failed


def save_comment(user_id, movie_id, comment_text):

    try:
        # Create a new Comment object
        new_comment = Comment(
            user_id=user_id, movie_id=movie_id, comment_text=comment_text
        )

        # Add the new comment to the database session
        db.session.add(new_comment)

        # Commit the changes to the database
        db.session.commit()

        return True  # Return True if successful
    except Exception as e:
        print(f"Error saving comment: {e}")
        db.session.rollback()  # Rollback the session in case of error
        return False  # Return False if unsuccessful


def add_comment():
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    try:
        title = request.form["title"]
        comment_text = request.form[
            "comment_text"
        ]  # Updated to retrieve 'comment_text'
        user_id = session.get("user_id")  # Get user ID from session
        movie_id = get_id_from_title(
            title
        )  # Assuming you have a function to get movie_id from title

        # Call the save_comment function to save the comment to the database
        if save_comment(user_id, movie_id, comment_text):
            return redirect(url_for("movie.movie_details", title=title))
        else:
            return (
                "Error saving comment",
                500,
            )  # Return an error message if unsuccessful
    except Exception as e:
        return (
            f"An error occurred: {e}",
            500,
        )  # Return an error message if an exception occurs


def submit_comment():
    try:
        # Call the add_comment function to handle the form submission
        return add_comment()
    except Exception as e:
        return f"An error occurred: {e}", 500


def save_rating(user_id, movie_id, rating):
    try:
        # Check if the user has already rated the movie
        existing_rating = MovieRating.query.filter_by(
            user_id=user_id, movie_id=movie_id
        ).first()

        if existing_rating:
            # Update the existing rating
            existing_rating.rating = rating
        else:
            # Create a new MovieRating object
            new_rating = MovieRating(user_id=user_id, movie_id=movie_id, rating=rating)
            # Add the new rating to the database session
            db.session.add(new_rating)

        # Commit the changes to the database
        db.session.commit()

        return True  # Return True if successful
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        return False  # Return False if unsuccessful


def rate_movie():
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    try:
        title = request.form["title"]
        user_id = session.get("user_id")  # Get user ID from session
        movie_id = get_id_from_title(
            title
        )  # Assuming you have a function to get movie_id from title
        rating = request.form["rating"]
        print(f"Received movie_id: {movie_id}, rating: {rating}")

        # Call the save_rating function to save the rating to the database
        if save_rating(user_id, movie_id, rating):
            return redirect(url_for("movie.movie_details", title=title))
        else:
            return "Error saving rating", 500  # Return an error message if unsuccessful

    except Exception as e:
        return (
            f"An error occurred: {e}",
            500,
        )  # Return an error message if an exception occurs


def submit_rating():
    try:
        return rate_movie()
    except Exception as e:
        return f"An error occurred: {e}", 500


def get_user_rating(user_id, movie_title):
    """
    Fetches the user's rating for the given movie title.

    Args:
        user_id (int): The ID of the user.
        movie_title (str): The title of the movie.

    Returns:
        int or None: The user's rating for the movie if it exists, otherwise None.
    """
    user_rating = MovieRating.query.filter_by(
        user_id=user_id, movie_id=get_id_from_title(movie_title)
    ).first()
    return user_rating.rating if user_rating else None


def get_user_comment(movie_title):
    # Get the movie ID from the title
    movie_id = get_id_from_title(movie_title)

    # Fetch all comments for the movie
    comments = (
        Comment.query.filter_by(movie_id=movie_id)
        .order_by(Comment.timestamp.desc())
        .all()
    )

    return comments


def get_user_infos(user_id):
    user_infos = User.query.filter_by(id=user_id).first()
    return user_infos


def update_user_infos(user_id, new_data):
    user = User.query.filter_by(id=user_id).first()

    if user:
        # Update user attributes based on new_data dictionary
        if "full_name" in new_data:
            user.full_name = new_data["full_name"]
        if "email" in new_data:
            user.email = new_data["email"]

        # Update password if a new password is provided
        if "password" in new_data:
            user.password = new_data["password"]

        # Update password hash if a new password hash is provided
        if "hashed_password" in new_data:
            user.password_hash = new_data["hashed_password"]

        # Commit changes to the database
        db.session.commit()
        return True
    else:
        return False
