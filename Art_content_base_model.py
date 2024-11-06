import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load the datasets
articles_df = pd.read_csv("combined_articles.csv")

# Combine title, description, and author into a single feature
combined_features = (articles_df["Title"] + " " + articles_df["Description"] + " " + articles_df["Author"])

# Define a TF-IDF Vectorizer Object. Remove all English stop words such as 'the', 'a'
# Additionally, set min_df and max_df parameters to filter out terms that appear too infrequently or too frequently
tfidf = TfidfVectorizer(min_df=2, max_df=0.7, stop_words="english")

# Construct the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(combined_features)

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Construct a reverse map of indices and article titles
indices = pd.Series(articles_df.index, index=articles_df["Title"]).drop_duplicates()

# Function that takes in user interactions (read articles and search query) and outputs personalized recommendations
def get_recommendations_with_user_interaction(user_read_articles, cosine_sim=cosine_sim):
    # Combine user interactions (read articles) to influence recommendations
    user_interactions = " ".join(user_read_articles)

    # Transform user interactions using the TF-IDF vectorizer
    user_interactions_tfidf = tfidf.transform([user_interactions])

    # Compute cosine similarity between user interactions and all articles
    cosine_sim_with_user = linear_kernel(user_interactions_tfidf, tfidf_matrix)

    # Sort articles based on the similarity scores with user interactions
    sim_scores_with_user = list(enumerate(cosine_sim_with_user[0]))
    sim_scores_with_user = sorted(sim_scores_with_user, key=lambda x: x[1], reverse=True)

    # Exclude articles that the user has already read
    sim_scores_with_user = [
        (idx, score)
        for idx, score in sim_scores_with_user
        if articles_df.iloc[idx]["Title"] not in user_read_articles
    ]

    # Get the indices of the top recommended articles
    article_indices = [i[0] for i in sim_scores_with_user[:10]]  # Get top 10 recommendations
    
    # Create a list of dictionaries containing information about the recommended articles
    recommended_articles = []
    for idx in article_indices:
        article_info = {
            "Title": articles_df.iloc[idx]["Title"],
            "Image": articles_df.iloc[idx]["Image"],
            "Description": articles_df.iloc[idx]["Description"],
            "Author": articles_df.iloc[idx]["Author"],
            "Link": articles_df.iloc[idx]["Link"]
        }
        recommended_articles.append(article_info)

    return recommended_articles
