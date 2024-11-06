import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
import pandas as pd
from cf import (
    user_based_collaborative_filtering,
    item_based_collaborative_filtering,
    neural_network_collaborative_filtering,
)

# # Load the ratings data
# ratings_data = pd.read_csv("ratings.csv")

# Simulating the structure of the 'ratings.csv' file based on the provided column names
ratings_data = pd.DataFrame({
    'userId': [1, 1, 2, 2, 3, 3],
    'movieId': [10, 20, 10, 30, 20, 30],
    'rating': [3.5, 4.0, 2.0, 5.0, 4.5, 3.0],
    'timestamp': [1112486027, 1112484676, 1112484819, 1112484727, 1112484580, 1112484661]
})

# Create user-item matrix
user_item_matrix = (
    ratings_data.pivot(index="userId", columns="movieId", values="rating")
    .fillna(0)
    .values
)

# Get list of movie IDs
movie_ids = ratings_data["movieId"].unique().tolist()


def evaluate_model(model_function, user_item_matrix, movie_ids, num_recommendations=10):
    train_data, test_data = train_test_split(
        user_item_matrix, test_size=0.2, random_state=42
    )
    true_ratings = []
    predicted_ratings = []

    for user_id in range(1, test_data.shape[0] + 1):
        recommended_movies = model_function(
            user_id, train_data, movie_ids, num_recommendations
        )
        for movie in recommended_movies:
            movie_id = movie["movie_id"]
            movie_index = movie_ids.index(movie_id)
            true_rating = test_data[user_id - 1, movie_index]
            predicted_rating = (
                train_data[user_id - 1, movie_index]
                if train_data[user_id - 1, movie_index] != 0
                else 0
            )
            true_ratings.append(true_rating)
            predicted_ratings.append(predicted_rating)

    mae = mean_absolute_error(true_ratings, predicted_ratings)
    rmse = mean_squared_error(true_ratings, predicted_ratings, squared=False)

    true_binary = [1 if rating > 0 else 0 for rating in true_ratings]
    predicted_binary = [1 if rating > 0 else 0 for rating in predicted_ratings]

    precision = precision_score(true_binary, predicted_binary, zero_division=1)
    recall = recall_score(true_binary, predicted_binary, zero_division=1)
    f1 = f1_score(true_binary, predicted_binary, zero_division=1)

    return {
        "MAE": mae,
        "RMSE": rmse,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
    }


# Evaluate User-based Collaborative Filtering
user_based_results = evaluate_model(
    user_based_collaborative_filtering, user_item_matrix, movie_ids
)
print("User-based Collaborative Filtering:", user_based_results)

# Evaluate Item-based Collaborative Filtering
item_based_results = evaluate_model(
    item_based_collaborative_filtering, user_item_matrix, movie_ids
)
print("Item-based Collaborative Filtering:", item_based_results)

# Evaluate Neural Network-based Collaborative Filtering
neural_network_results = evaluate_model(
    neural_network_collaborative_filtering, user_item_matrix, movie_ids
)
print("Neural Network-based Collaborative Filtering:", neural_network_results)



