import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_slashfilm():
    url = "https://www.slashfilm.com/category/movie-news/"
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "article-item")))
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    article_items = soup.find_all("li", class_="article-item")
    base_url = "https://www.slashfilm.com"
    for item in article_items:
        article_title = item.find("h3").text.strip() if item.find("h3") else None
        article_description = (
            item.find("div", class_="article-preview").text.strip()
            if item.find("div", class_="article-preview")
            else None
        )
        article_link = item.find("a")["href"] if item.find("a") else None
        article_link = base_url + article_link if article_link else None
        article_image = item.find("img")["src"] if item.find("img") else None
        article_author = (
            item.find("div", class_="more-article-info").span.text.strip()
            if item.find("div", class_="more-article-info")
            else None
        )
        articles.append(
            {
                "Title": article_title,
                "Description": article_description,
                "Author": article_author,
                "Link": article_link,
                "Image": article_image,
            }
        )
    df = pd.DataFrame(articles)
    
    output_file = "slashfilm.csv"
    if output_file:
        df.to_csv(output_file, index=False)
    return df
