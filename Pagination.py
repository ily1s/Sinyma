from math import ceil

# Function to split articles into chunks/pages
def paginate_articles(articles, page_size):
    num_pages = ceil(len(articles) / page_size)
    paginated_articles = []
    for i in range(num_pages):
        start_idx = i * page_size
        end_idx = (i + 1) * page_size
        paginated_articles.append(articles[start_idx:end_idx])
    return paginated_articles

