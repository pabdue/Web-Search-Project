import requests
from bs4 import BeautifulSoup
from queue import Queue
from pymongo import MongoClient
from urllib.parse import urljoin

client = MongoClient('mongodb://localhost:27017/')
db = client.civilCrawler
pages_collection = db.civilProfs

def is_target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('div', class_='fac-info')

def retrieve_url(url):
    # Skip "mailto" links and specific URLs causing errors
    if url.startswith("mailto:") or url.startswith("tel:") or url.startswith("javascript:") or url in ["https://maps.cpp.edu/", "https://services.engineering.cpp.edu/Ticket"]:
        return None

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        print(f"Error retrieving URL {url}: {e}")
    return None

def store_page(url, html):
    pages_collection.insert_one({'url': url, 'html': html})

def parse_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return [urljoin(base_url, link['href']) for link in links]

def crawler_thread(frontier, base_url, num_pages_to_persist):
    visited_urls = set()
    pages_persisted = 0

    while not frontier.empty() and pages_persisted < num_pages_to_persist:
        url = frontier.get()

        if url not in visited_urls:
            visited_urls.add(url)

            html = retrieve_url(url)
            if html:
                if is_target_page(html):
                    store_page(url, html)
                    pages_persisted += 1
                    print(f"Persisted URL: {url}")
                for link in parse_html(html, base_url):
                    if link not in visited_urls:
                        frontier.put(link)

    print(f"Crawling is done. Total pages persisted: {pages_persisted}")

frontier = Queue()
base_url = 'https://www.cpp.edu/engineering/ce/index.shtml'
frontier.put(base_url)

# Specify the number of pages to persist
num_pages_to_persist = 25  # Change this to your desired number

crawler_thread(frontier, base_url, num_pages_to_persist)
