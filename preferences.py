from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Preference
import pandas as pd
import json

df = pd.read_csv("movie_data.csv")
df.dropna(subset=["Poster_Path"], how="any", inplace=True)
suggested_movies = list(df["Title"])


preferences_bp = Blueprint("preferences", __name__)


@preferences_bp.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "POST":
        # Get the current user's ID from the session
        user_id = session.get("user_id")

        # Get form data
        favorite_movie1 = request.form["favorite_movie1"]
        favorite_movie2 = request.form["favorite_movie2"]
        favorite_movie3 = request.form["favorite_movie3"]
        actor = request.form["actor"]
        genre = request.form.getlist("genre")
        themes = request.form.getlist("themes")

        # Convert lists to JSON strings
        genre_json = json.dumps(genre)
        themes_json = json.dumps(themes)

        # Create a new Preference object
        preference = Preference(
            user_id=user_id,
            favorite_movie1=favorite_movie1,
            favorite_movie2=favorite_movie2,
            favorite_movie3=favorite_movie3,
            actor=actor,
            genre=genre_json,
            themes=themes_json,
        )

        # Add the preference to the database
        db.session.add(preference)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("preferences.html", suggestedMovies=suggested_movies)
