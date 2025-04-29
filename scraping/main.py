from multiprocessing import process
import requests
from markdownify import MarkdownConverter
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re
import os


FILE_SAVE_LOCATION = './all_files'

visited = set()
broken_urls = set()
futures = list()

def sanitize_filename(title):
    return re.sub(r'[^\w\-_. ]', '', title).strip().replace(' ', '_')


def get_md_filename(title, url):
    title = title.string if title else ""

    path = urlparse(url).path
    name = os.path.basename(path) or 'index'

    return sanitize_filename(f"{title}_{name}") + '.md'


def get_pdf_filename(url):
    path = urlparse(url).path
    name = os.path.basename(path) or 'index'
    return sanitize_filename(name) + '.pdf'


def save_pdf(filename, content):
    with open(os.path.join(FILE_SAVE_LOCATION, filename), "wb") as f:
        f.write(content)


def save_as_md(article, filename):
    # soup zu markdown konviertieren
    md_text = MarkdownConverter().convert_soup(article)

    # Formatierung der Überschriften korrigieren
    md_text = md_text.replace("[### \n", "### [")
    md_text = md_text.replace("[## \n", "## [")
    md_text = md_text.replace("[# \n", "# [")

    # Erstellung der output markdown datei
    with open(os.path.join(FILE_SAVE_LOCATION, filename), 'w', encoding='utf-8') as out_f:
        out_f.write(md_text)


def clean_soup(soup):
    # elemente die aus DOM entfernt werden sollen
    for s in soup.select('#km1-search-dialog, figcaption, .km1-figure__caption-credit, .km1-breadcrumbs, figure, script, style, .km1-article-services, .km1-language-selector, .km1-article-preview__read-more, .km1-accordion-item__toggle-button, #psfCheck'):
        s.extract()

    # elemente die seperators bekommen sollen
    sections = list(soup.select('.km1-service-teaser, .km1-teaser'))
    for i, section in enumerate(sections[:-1]):
        hr_after = soup.new_tag('hr')
        section.insert_after(hr_after)

    # format list items in service teaser
    for list_container in soup.select('.km1-service-teaser__list'):
        ul = soup.new_tag('ul')
        for item in list_container.select('.km1-service-teaser__list-item'):
            li = soup.new_tag('li')
            li.string = item.get_text(strip=True)
            ul.append(li)
        list_container.replace_with(ul)
    
    return soup.main


def process_new_url(url, depth, new_url):
    absolute_link = urljoin(url, new_url['href'])
    absolute_link = absolute_link.strip()
    absolute_link = absolute_link.split('#')[0]  # Remove anchors
    absolute_link = absolute_link.split('?')[0]  # Remove query parameters
    absolute_link = absolute_link.rstrip('/')
    absolute_link = absolute_link.rstrip('/n0')

    if (urlparse(absolute_link).netloc != urlparse(url).netloc and "https://fhh" not in absolute_link) or absolute_link in visited:
        return

    if 'https://www.hamburg.de/service/' in absolute_link:
        scrape(absolute_link, 0)
    else:
        scrape(absolute_link, depth + 1)


def scrape(url, depth=0, max_depth=100):
    print(f"{'  ' * depth}{url}")
    visited.add(url)

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            broken_urls.add(url)
            return

        if url[-4:] == ".pdf":
            filename = get_pdf_filename(url[:-4])
            save_pdf(filename, response.content)
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article = clean_soup(soup)

        if depth >= max_depth or article is None:
            return
        
        filename = get_md_filename(soup.title, url)
        save_as_md(article, filename)
        
        new_urls = article.find_all('a', href=True)
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures.extend([executor.submit(lambda x: process_new_url(url, depth, x), new_url) for new_url in new_urls])
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        broken_urls.add(url)


def export_urls_to_json(filename="urls_to_scrape.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(visited, f, indent=4)

    with open("broken_links.json", 'w') as f:
        json.dump(broken_urls, f)

    print(f"Url list exported to {filename}")


"""
    Scrapes all urls under hamburg.de/service/, including containing pdf files and linked webpages of hamburg.de
"""
def main():
    # Example usage:
    start_url = 'https://www.hamburg.de/service/'
    scrape(start_url)
    export_urls_to_json()

    while(True):
        for future in as_completed(futures):
            print(future.result())
        time.sleep(0.5)
        if len(futures) == 0:
            return


if __name__ == "__main__":
    main()