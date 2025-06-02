"""Dieses Script dient zum Scrapen der Websiteinhalte von hamburg.de/services inkl. verlinkten Seiten und Dateien"""

import os
import shutil
import time
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
from markdownify import MarkdownConverter
from tqdm import tqdm

from rag_pipeline.constants import DATA_PATH, SCRAPED_URLS_FILE, SCRAPED_BROKEN_LINKS_FILE, DATASET_SOURCES_PATH


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


def save_pdf(filename, usecase, content):
    with open(os.path.join(DATA_PATH, usecase, filename), "wb") as f:
        f.write(content)


def save_as_md(article, usecase, filename):
    # soup zu markdown konviertieren
    md_text = MarkdownConverter().convert_soup(article)

    # Formatierung der Überschriften korrigieren
    md_text = md_text.replace("[### \n", "### [")
    md_text = md_text.replace("[## \n", "## [")
    md_text = md_text.replace("[# \n", "# [")

    # clean of whitespace
    md_text = md_text.strip()
    md_text = re.sub(r"\n{2,}", "\n", md_text)

    # Erstellung der output markdown datei
    with open(os.path.join(DATA_PATH, usecase, filename), 'w', encoding='utf-8') as out_f:
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


def process_new_url(url, usecase, new_url):
    absolute_link = urljoin(url, new_url['href'])
    absolute_link = absolute_link.strip()
    absolute_link = absolute_link.split('#')[0]  # Remove anchors
    absolute_link = absolute_link.split('?')[0]  # Remove query parameters
    absolute_link = absolute_link.rstrip('/')
    absolute_link = absolute_link.rstrip('/n0')

    if (urlparse(absolute_link).netloc != urlparse(url).netloc and "https://fhh" not in absolute_link) or absolute_link in visited:
        return
    
    if absolute_link[-4:] != ".pdf":
        return

    scrape(absolute_link, usecase)


def scrape(url, usecase):
    visited.add(url)
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            raise Exception(f"Error - Response Code {response.status_code}")

        if url[-4:] == ".pdf":
            filename = get_pdf_filename(url[:-4])
            save_pdf(filename, usecase, response.content)
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article = clean_soup(soup)

        if article is None:
            return
        
        filename = get_md_filename(soup.title, url)
        save_as_md(article, usecase, filename)
        
        new_urls = article.find_all('a', href=True)
        for new_url in new_urls:
            process_new_url(url, usecase, new_url)
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        broken_urls.add(url)

def load_source_urls():
    with open(DATASET_SOURCES_PATH) as f:
        return json.load(f)

"""
    Scrapes all urls for each usecase
"""
def main():
    source_urls = load_source_urls()

    if os.path.exists(DATA_PATH):
        shutil.rmtree(DATA_PATH)

    os.mkdir(DATA_PATH)

    for usecase, urls in source_urls.items():
        os.mkdir(os.path.join(DATA_PATH, usecase))
        
        for url in tqdm(urls, desc=usecase):
            scrape(url, usecase)
            time.sleep(0.1)
        for url in set(broken_urls):
            scrape(url, usecase)
            time.sleep(0.1)
        broken_urls.clear()


if __name__ == "__main__":
    main()