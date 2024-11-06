import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from basic_functions import get_title_from_id
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

# Read movie data from CSV file
movie_data = pd.read_csv("movie_data.csv")
movie_data.dropna(subset=["Poster_Path"], how="any", inplace=True)


def user_based_collaborative_filtering(
    user_id, user_item_matrix, movie_ids, num_recommendations=10
):
    """
    User-based collaborative filtering function to generate movie recommendations for a user.

    Args:
    - user_id: ID of the target user for whom recommendations are generated.
    - user_item_matrix: User-item interaction matrix where rows represent users and columns represent items.
    - movie_ids: List of movie IDs corresponding to the columns of the user_item_matrix.
    - num_recommendations: Number of recommendations to generate for the user.

    Returns:
    - recommended_movies: List of recommended movie IDs.
    """

    # Find the index of the target user
    user_index = user_id - 1  # Assuming user IDs start from 1

    # Compute similarity between the target user and all other users
    user_similarities = cosine_similarity(
        user_item_matrix[user_index, np.newaxis], user_item_matrix
    )

    # Sort the similarities and get the indices of top similar users
    similar_users_indices = np.argsort(user_similarities)[0][::-1][
        1:
    ]  # Exclude the target user

    # Get the items that similar users have interacted with but the target user hasn't
    recommended_items = np.where(
        user_item_matrix[user_index] == 0, 1, 0
    ) * user_item_matrix[similar_users_indices].sum(axis=0)

    # Get the indices of recommended items sorted by their scores
    recommended_items_indices = np.argsort(recommended_items)[::-1]

    # Filter out items that the target user has already interacted with
    recommended_movies = [
        movie_ids[i]
        for i in recommended_items_indices
        if user_item_matrix[user_index, i] == 0
    ][:num_recommendations]

    return recommended_movies


def item_based_collaborative_filtering(
    user_id, user_item_matrix, movie_ids, num_recommendations=10
):
    """
    Item-based collaborative filtering function to generate movie recommendations for a user.

    Args:
    - user_id: ID of the target user for whom recommendations are generated.
    - user_item_matrix: User-item interaction matrix where rows represent users and columns represent items.
    - movie_ids: List of movie IDs corresponding to the columns of the user_item_matrix.
    - num_recommendations: Number of recommendations to generate for the user.

    Returns:
    - recommended_movies: List of recommended movie IDs.
    """

    # Transpose the user-item matrix to get item-user matrix
    item_user_matrix = user_item_matrix.T

    # Find the index of the target user
    user_index = user_id - 1  # Assuming user IDs start from 1

    # Compute similarity between items (movies)
    item_similarities = cosine_similarity(
        item_user_matrix[:, user_index, np.newaxis].T, item_user_matrix.T
    )

    # Sort the similarities and get the indices of top similar items
    similar_items_indices = np.argsort(item_similarities)[0][::-1][
        1:
    ]  # Exclude the target item

    # Get the indices of recommended items sorted by their scores
    recommended_items_indices = [
        i for i in similar_items_indices if user_item_matrix[i, user_index] == 0
    ][:num_recommendations]

    # Get the recommended movie IDs
    recommended_movies = [movie_ids[i] for i in recommended_items_indices]

    return recommended_movies


def collaborative_filtering(
    user_id, user_item_matrix, movie_ids, num_recommendations=10
):
    """
    Combined collaborative filtering function to generate movie recommendations for a user.

    Args:
    - user_id: ID of the target user for whom recommendations are generated.
    - user_item_matrix: User-item interaction matrix where rows represent users and columns represent items.
    - movie_ids: List of movie titles corresponding to the columns of the user_item_matrix.
    - num_recommendations: Number of recommendations to generate for the user.

    Returns:
    - recommended_movies: List of recommended movie dictionaries with complete information.
    """
    if user_id <= 0 or user_id > user_item_matrix.shape[0]:
        # If the user_id is out of bounds, return an empty list
        return []

    # Get user-based recommendations
    user_based_recommendations = user_based_collaborative_filtering(
        user_id, user_item_matrix, movie_ids, num_recommendations
    )

    # Get item-based recommendations
    item_based_recommendations = item_based_collaborative_filtering(
        user_id, user_item_matrix, movie_ids, num_recommendations
    )

    # Combine recommendations from both approaches (remove duplicates)
    combined_recommendations = list(
        set(user_based_recommendations + item_based_recommendations)
    )

    # Retrieve movie details for the combined recommendations
    recommended_movies = []
    for movie_title in combined_recommendations:
        movie_title = get_title_from_id(movie_title)
        # Retrieve movie details from the movie_data DataFrame
        movie_details = movie_data.loc[movie_data["Title"] == movie_title].iloc[0]
        recommended_movies.append(
            {
                "Title": movie_details["Title"],
                "Poster_Path": movie_details["Poster_Path"],
                "Tagline": movie_details["Tagline"],
            }
        )

    return recommended_movies[:num_recommendations]


def neural_network_collaborative_filtering(
    user_id, user_item_matrix, movie_ids, num_recommendations=10
):
    """
    Neural network collaborative filtering function to generate movie recommendations for a user.

    Args:
    - user_id: ID of the target user for whom recommendations are generated.
    - user_item_matrix: User-item interaction matrix where rows represent users and columns represent items.
    - movie_ids: List of movie IDs corresponding to the columns of the user_item_matrix.
    - num_recommendations: Number of recommendations to generate for the user.

    Returns:
    - recommended_movies: List of recommended movie dictionaries with complete information.
    """
    if user_id <= 0 or user_id > user_item_matrix.shape[0]:
        # If the user_id is out of bounds, return an empty list
        return []

    # Split the data into training and testing sets
    train_data, test_data = train_test_split(
        user_item_matrix, test_size=0.2, random_state=42
    )

    # Initialize the neural network regressor
    neural_network = MLPRegressor(hidden_layer_sizes=(100,), max_iter=100)

    # Train the neural network
    neural_network.fit(train_data, train_data)

    # Predict ratings for the target user using the trained model
    user_ratings = neural_network.predict(
        test_data[user_id - 1].reshape(1, -1)
    ).flatten()
    user_ratings = np.asarray(user_ratings)

    # Sort the predicted ratings and get the indices of top rated items
    top_rated_indices = user_ratings.argsort()[::-1]

    # Filter out items that the target user has already interacted with
    recommended_movies = [
        {
            "movie_id": movie_ids[i],
            "Title": get_title_from_id(movie_ids[i]),
            "Poster_Path": movie_data.loc[movie_data["id"] == movie_ids[i]][
                "Poster_Path"
            ].values[0],
            "Tagline": movie_data.loc[movie_data["id"] == movie_ids[i]][
                "Tagline"
            ].values[0],
        }
        for i in top_rated_indices
        if test_data[user_id - 1, i] == 0
    ][:num_recommendations]

    return recommended_movies
