from markdownify import MarkdownConverter
from bs4 import BeautifulSoup
import json
import requests


with open("website_structure.json") as f:
    data = json.load(f)

url = "https://www.hamburg.de/service/info/111112920" # list(data.keys())[3]
response = requests.get(url, timeout=5)
soup = BeautifulSoup(response.text, 'html.parser')

if soup is None:
    print("No Document found!")

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

# soup zu markdown konviertieren
md_text = MarkdownConverter().convert_soup(soup.main)

# Formatierung der Überschriften korrigieren
md_text = md_text.replace("[### \n", "### [")
md_text = md_text.replace("[## \n", "## [")
md_text = md_text.replace("[# \n", "# [")

# Erstellung der output markdown datei
with open("output.md", 'w', encoding='utf-8') as out_f:
    out_f.write(md_text)
