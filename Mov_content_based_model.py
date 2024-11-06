import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from ast import literal_eval

# Load data
df = pd.read_csv("movie_data.csv")


# Clean and preprocess overview data
df["Overview"] = df["Overview"].fillna("")

# TF-IDF Vectorization
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["Overview"])

# Compute cosine similarity matrix based on TF-IDF matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)



# Parse features into python objects
features = ["Cast", "Keywords"]
for feature in features:
    df[feature] = df[feature].apply(literal_eval)


# Function to extract list of elements
def get_list(x):
    if isinstance(x, list):
        return [i["name"] for i in x]
    return []


# Apply functions to relevant features

features = ["Cast", "Keywords"]
for feature in features:
    df[feature] = df[feature].apply(get_list)


# Function to clean data
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    elif isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    else:
        return ""


# Apply clean_data function to features
features = ["Cast", "Keywords", "Director", "Genres"]
for feature in features:
    df[feature] = df[feature].apply(clean_data)


# Create 'soup' feature
def create_soup(x):
    return (
        " ".join(x["Keywords"])
        + " "
        + " ".join(x["Cast"])
        + " "
        + x["Director"]
        + " "
        + " ".join(x["Genres"])
    )


df["soup"] = df.apply(create_soup, axis=1)

# Count Vectorization
count = CountVectorizer(stop_words="english")
count_matrix = count.fit_transform(df["soup"])

# Compute the Cosine Similarity matrix based on the count_matrix

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# combine the two matrix of similarity

# Compute the Hadamard product of the two cosine similarity matrices
combined_cosine_sim = np.multiply(cosine_sim, cosine_sim2)
# Apply a threshold to the combined matrix


def get_recommendations(
    favorite_list,
    visited_list,
    watched_list,
    liked_list,
    wish_list,
    cosine_sim_matrix=combined_cosine_sim,
    columns=None,
):
    # Define coefficients for each list type
    coeff_favorite = 1.5
    coeff_visited = 1.0
    coeff_watched = 1.25
    coeff_liked = 1.5
    coeff_wish = 1.75

    # Initialize an array to store combined similarity scores
    combined_sim_scores = np.zeros(len(df))

    # Helper function to find index of a movie by title
    def find_movie_index(movie_title):
        try:
            idx = df[df["Title"] == movie_title]['index'].tolist()[0]
            return idx
        except IndexError:
            return None

    # Accumulate similarity scores from favorite list if not empty
    if favorite_list:
        for movie_title in favorite_list:
            idx = find_movie_index(movie_title)
            if idx is not None:
                sim_scores = cosine_sim_matrix[idx]
                combined_sim_scores += coeff_favorite * sim_scores
    # Accumulate similarity scores from visited list if not empty
    if visited_list:
        for movie_title in visited_list:
            idx = find_movie_index(movie_title)
            if idx is not None:
                sim_scores = cosine_sim_matrix[idx]
                combined_sim_scores += coeff_visited * sim_scores

    # Accumulate similarity scores from watched list if not empty
    if watched_list:
        for movie_title in watched_list:
            idx = find_movie_index(movie_title)
            if idx is not None:
                sim_scores = cosine_sim_matrix[idx]
                combined_sim_scores += coeff_watched * sim_scores

    # Accumulate similarity scores from liked list if not empty
    if liked_list:
        for movie_title in liked_list:
            idx = find_movie_index(movie_title)
            if idx is not None:
                sim_scores = cosine_sim_matrix[idx]
                combined_sim_scores += coeff_liked * sim_scores

    # Accumulate similarity scores from wish list if not empty
    if wish_list:
        for movie_title in wish_list:
            idx = find_movie_index(movie_title)
            if idx is not None:
                sim_scores = cosine_sim_matrix[idx]
                combined_sim_scores += coeff_wish * sim_scores

    # Sort indices based on combined similarity scores
    movie_indices = np.argsort(combined_sim_scores)[::-1]

    # Get top 10 movie indices (excluding the input movies themselves)
    input_movie_titles = (
        visited_list + watched_list + liked_list + wish_list + favorite_list
    )
    if input_movie_titles:
        recommended_movie_indices = [
            idx
            for idx in movie_indices
            if df.iloc[idx]["Title"] not in input_movie_titles
        ][:10]
    else:
        # If all lists are empty, recommend top 10 popular movies by default
        recommended_movie_indices = (
            df["Popularity"].sort_values(ascending=False).head(10).index
        )

    # Get recommended movie rows (DataFrame rows)
    if columns:
        recommended_movies = df.iloc[recommended_movie_indices][columns].to_dict(
            orient="records"
        )
    else:
        recommended_movies = df.iloc[recommended_movie_indices].to_dict(
            orient="records"
        )

    return recommended_movies
