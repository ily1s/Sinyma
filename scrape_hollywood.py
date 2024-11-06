import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

def scrape_hollywood():
    url = "https://www.hollywoodreporter.com/c/movies"
    def scrape_page(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            stories = soup.find_all("div", class_="story")
            data = []
            for story in stories:
                title_elem = story.find("h3", class_="c-title")
                title = title_elem.text.strip()
                link = title_elem.find("a")["href"]
                description_elem = story.find("p", class_="c-dek")
                description = description_elem.text.strip()
                author_elem = story.find("div", class_="c-tagline")
                author = author_elem.text.strip()
                image_elem = story.find("div", class_="c-lazy-image").find("img")[
                    "data-lazy-src"
                ]
                data.append([title, description, author, link, image_elem])
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            return []

    def scrape_multiple_pages(base_url, num_pages):
        all_data = []
        for page_num in range(1, num_pages + 1):
            url = f"{base_url}/page/{page_num}/"
            print(f"Scraping data from page {page_num}...")
            data = scrape_page(url)
            all_data.extend(data)
            time.sleep(1)
        print("Scraping completed.")
        df = pd.DataFrame(
            all_data, columns=["Title", "Description", "Author", "Link", "Image"]
        )
        return df

    base_url = url
    num_pages = 100
    df = scrape_multiple_pages(base_url, num_pages)
    output_file = "hollywood.csv"
    if output_file:
        df.to_csv(output_file, index=False)
    return df

