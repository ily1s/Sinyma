from flask import (
    render_template,
    request,
    Blueprint,
    session,
    jsonify,
    redirect,
    url_for,
)
from Scraping import load_articles_from_file, search_articles
from Pagination import paginate_articles
from Art_content_base_model import get_recommendations_with_user_interaction
from models import UserInteraction, db, User
import json
import random
from collections import defaultdict
from urllib.parse import urlparse

# Define a Blueprint for the movie_news route
movie_news_bp = Blueprint("movie_news", __name__)


def get_base_link(url):
    parsed_url = urlparse(url)
    base_link = parsed_url.scheme + "://" + parsed_url.netloc
    return base_link


# Define the route to record user interactions
@movie_news_bp.route("/record_interaction", methods=["POST"])
def record_interaction():
    if request.method == "POST":
        article_title = request.form.get("article_title")
        if article_title:
            if "user_id" in session:
                user_id = session["user_id"]
                user_interaction = UserInteraction.query.filter_by(
                    user_id=user_id
                ).first()

                if user_interaction:
                    read_articles = json.loads(user_interaction.read_articles)
                    # # Check if article title is already in the list
                    # if article_title not in read_articles:
                    #     read_articles.append(article_title)
                    #     user_interaction.read_articles = json.dumps(read_articles)
                    # else:
                    #     # Article title already exists, no need to add it again
                    #     pass
                    read_articles.append(article_title)
                    user_interaction.read_articles = json.dumps(read_articles)
                else:
                    user_interaction = UserInteraction(
                        user_id=user_id, read_articles=json.dumps([article_title])
                    )
                try:
                    db.session.add(user_interaction)
                    db.session.commit()
                    return redirect(url_for("movie_news.movie_news"))
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"error": str(e)}), 500
            else:
                return jsonify({"error": "User is not logged in"}), 401
        else:
            return jsonify({"error": "Article title not provided"}), 400


@movie_news_bp.route("/movie_news", methods=["GET", "POST"])
def movie_news():
    # Define the number of articles per page
    ARTICLES_PER_PAGE = 15  # Adjust as needed
    articles = load_articles_from_file()
    paginated_articles = paginate_articles(articles, ARTICLES_PER_PAGE)
    num_pages = len(paginated_articles)
    current_page = int(request.args.get("page", 1))
    username = None 
    if request.method == "POST":
        user_id = session.get("user_id")
        if user_id:
            user = User.query.filter_by(id=user_id).first() 
            if user:
                username = user.full_name
                
        search_query = request.form.get("search")
        if search_query:
            searched_articles = search_articles(articles, search_query)
            return render_template(
                "movie_news_search.html",
                articles=searched_articles,
                num_pages=0,
                search=search_query,
                username=username
            )

    # Fetch user ID from the session
    user_id = session.get("user_id")
    username = None
    if user_id:
        user = User.query.filter_by(id=user_id).first() 
        if user:
            username = user.full_name
        # Fetch user read articles from the database
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).first()
        if user_interactions:
            user_read_articles = json.loads(user_interactions.read_articles)
        else:
            user_read_articles = []

        # Generate personalized recommendations using user interactions
        recommended_articles = get_recommendations_with_user_interaction(
            user_read_articles
        )

    else:
        # If there are no user interactions, set recommended_articles to an empty list
        recommended_articles = []

    # Extract base links and store articles by base link
    articles_by_base_link = defaultdict(list)
    for article in articles:
        base_link = get_base_link(article["Link"])
        articles_by_base_link[base_link].append(article)

    # Find the newest article (first article for each base link)
    newest_articles = []
    for base_link, articles in articles_by_base_link.items():
        newest_article = articles[
            0
        ]  # Assuming the first article for each base link is the newest
        newest_articles.append(newest_article)

    # Limit the number of articles to 3
    newest_articles = newest_articles[:3]

    # Shuffle the articles before rendering
    random.shuffle(paginated_articles)

    return render_template(
        "movie_news.html",
        articles=paginated_articles[current_page - 1],
        num_pages=num_pages,
        current_page=current_page,
        recommended_articles=recommended_articles,
        newest_articles=newest_articles,
        username = username,
    )
