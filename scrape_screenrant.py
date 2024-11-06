import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_screenrant():
    url = "https://screenrant.com/movie-news/"
    driver = webdriver.Chrome()
    articles = []
    for i in range(1, 50):
        page_url = f"{url}/{i}/"
        driver.get(page_url)
        articles_div = driver.find_elements(By.CLASS_NAME, "display-card")
        for article in articles_div:
            art_tag = article.find_element(By.TAG_NAME, "h5")
            art_img = article.find_element(By.TAG_NAME, "img").get_attribute("src")
            art_url = art_tag.find_element(By.TAG_NAME, "a").get_attribute("href")
            art_title = art_tag.text
            art_abstract = article.find_element(
                By.CLASS_NAME, "display-card-excerpt"
            ).text
            art_author_element = article.find_element(By.CLASS_NAME, "w-author-name")
            art_author = art_author_element.find_element(By.TAG_NAME, "a").text.strip()

            articles.append(
                {
                    "Title": art_title,
                    "Description": art_abstract,
                    "Author": art_author,
                    "Link": art_url,
                    "Image": art_img,
                }
            )
    driver.quit()
    df = pd.DataFrame(articles)
    output_file = "screenrant.csv"
    if output_file:
        df.to_csv(output_file, index=False)
    return df

