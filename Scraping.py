import pandas as pd
from scrape_slashfilm import scrape_slashfilm
from scrape_hollywood import scrape_hollywood
from scrape_screenrant import scrape_screenrant

import os


def scrape_articles():
    # Scrape Slashfilm
    slashfilm_df = scrape_slashfilm()

    # Scrape Screenrant
    screenrant_df = scrape_screenrant()

    # Scrape Hollywood Reporter
    hollywood_df = scrape_hollywood()

    print("Scraping completed.")

    # Combine all DataFrames into one
    combined_df = pd.concat(
        [slashfilm_df, hollywood_df, screenrant_df], ignore_index=True
    )

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv("combined_articles.csv", index=False)


def update_articles():
    scrape_articles()


# Load articles from combined CSV file
def load_articles_from_file():
    if not os.path.isfile("combined_articles.csv"):
        # If the CSV file doesn't exist, scrape the articles
        scrape_articles()

    try:
        df = pd.read_csv("combined_articles.csv")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []


def search_articles(articles, query):
    # Filter articles based on the query (you can customize the search logic here)
    return [
        article for article in articles if query.lower() in article["Title"].lower()
    ]
