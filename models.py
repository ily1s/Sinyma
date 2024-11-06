from flask_sqlalchemy import SQLAlchemy

# Initialize a SQLAlchemy object
db = SQLAlchemy()


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    favorite_movie1 = db.Column(db.String(100))
    favorite_movie2 = db.Column(db.String(100))
    favorite_movie3 = db.Column(db.String(100))
    actor = db.Column(db.String(100))
    genre = db.Column(db.String(255))
    themes = db.Column(db.String(255))

    user = db.relationship("User", backref="preferences")


class UserInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    read_articles = db.Column(db.Text)

    user = db.relationship("User", backref="interactions")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.now())

    user = db.relationship("User", backref="comments")


class MovieRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref="ratings")


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    watch_mov = db.Column(db.String(100))

    user = db.relationship("User", backref="watchlist")


class likedlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    liked_mov = db.Column(db.String(100))

    user = db.relationship("User", backref="likedlist")


class wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    wish_mov = db.Column(db.String(100))

    user = db.relationship("User", backref="wishlist")


class visitedlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    visited_mov = db.Column(db.String(100))

    user = db.relationship("User", backref="visitedlist")
