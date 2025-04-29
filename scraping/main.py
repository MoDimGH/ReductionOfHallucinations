import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

visited = set()

def scrape(url, depth=0):
    time.sleep(0.5)
    if depth > max_depth or url in visited:
        return

    visited.add(url)
    print("  " * depth + url)

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            absolute_link = urljoin(url, link['href'])
            absolute_link = absolute_link.split('#')[0]  # Remove anchors
            absolute_link = absolute_link.split('?')[0]  # Remove query parameters
            absolute_link = absolute_link.rstrip('/')

            print(urlparse(absolute_link).geturl())
            if urlparse(absolute_link).netloc == urlparse(url).netloc and 'https://www.hamburg.de/service/' in urlparse(absolute_link).geturl():
                scrape(absolute_link, depth + 1)
    except Exception as e:
        print(f"Error scraping {url}: {e}")


def export_to_json(filename="urls_to_scrape.json"):
    structure = {}

    for parent, child in graph.edges():
        if parent not in structure:
            structure[parent] = []
        structure[parent].append(child)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=4)

    print(f"Graph exported to {filename}")


"""
    Scrapes all urls under hamburg.de/service/, including containing pdf files and linked webpages of hamburg.de
"""
def main():
    # Example usage:
    start_url = 'https://www.hamburg.de/service/'
    scrape(start_url)
    export_to_json()


if __name__ == "__main__":
    main()