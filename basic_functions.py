import pandas as pd
from ast import literal_eval
from fuzzywuzzy import process, fuzz

df = pd.read_csv("movie_data.csv")

df_articles = pd.read_csv("combined_articles.csv")



def splitting(x):
    if pd.isna(x):
        return []
    return x.split(",")


df["spoken_languages"] = df["spoken_languages"].apply(splitting)


def get_popular_movies():
    df2 = df.sort_values(["Popularity"], ascending=False)
    return df2


def get_top_rated_movies():
    mean_vote = df["Vote_Average"].mean()
    df3 = df[(df["Vote_Average"] > mean_vote) & (df["Vote_Count"] >= 1000)].sort_values(
        ["Vote_Average"], ascending=False
    )
    return df3


def get_list2(x):
    if isinstance(x, list):
        return [i["name"] for i in x], [i["character"] for i in x]
    return [], []


def get_list_cast(movie_select):
    movie_row = df[df["Title"] == movie_select]
    movie_row["Cast"] = movie_row["Cast"].apply(literal_eval).apply(get_list2)
    return movie_row["Cast"]


def get_infos_from_title(title):
    infos = df[df["Title"] == title].iloc[0]
    return infos


def get_id_from_title(title):
    # Filter DataFrame based on the movie title and retrieve the first ID
    id = df.loc[df["Title"] == title, "id"].drop_duplicates().iloc[0]
    return int(id)


def get_title_from_id(movie_id):
    # Filter DataFrame based on the movie ID and retrieve the first Title
    title = df.loc[df["id"] == movie_id, "Title"].drop_duplicates().iloc[0]
    return title


def search_movies_from_text(input_text, threshold=70, num_results=30):
    """ "
    - threshold (int, optional): Minimum similarity score (0-100) for fuzzy matching. Default is 70.
    - num_results (int, optional): Maximum number of results to return. Default is 10.

    Returns:
    - list of tuples: List of (movie_title, similarity_score) for close matches.
    """
    # Extract movie titles from DataFrame
    movie_titles = df["Title"].tolist()

    # Perform fuzzy matching to find close matches
    matches = process.extract(input_text, movie_titles, limit=num_results)

    # Filter matches based on similarity threshold
    close_matches = [(title, score) for title, score in matches if score >= threshold]

    # Get movie titles from close_matches
    matched_titles = [title for title, score in close_matches]

    # Filter DataFrame to include only matched movies
    matched_movies_df = df[df["Title"].isin(matched_titles)]

    # Sort matched movies by similarity score and additional criteria (e.g., length of title)
    matched_movies_df["SimilarityScore"] = matched_movies_df["Title"].apply(
        lambda x: fuzz.token_set_ratio(input_text, x)
    )
    matched_movies_df = matched_movies_df.sort_values(
        by=["SimilarityScore", "Title"], ascending=[False, True]
    )

    # Reset the index of the DataFrame
    matched_movies_df.reset_index(drop=True, inplace=True)

    return matched_movies_df.to_dict(orient="records")


# function for articles history
def get_article_infos_from_title(title):
    if df_articles.empty or "Title" not in df_articles.columns:
        # Handle empty DataFrame or missing column
        return None

    matching_rows = df_articles[df_articles["Title"] == title]
    if not matching_rows.empty:
        # If matching rows exist, return info from the first row
        return matching_rows.iloc[0]
    else:
        # Handle case where no matching rows are found
        return None
