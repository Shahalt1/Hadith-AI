import requests 
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from helper_utilities import get_contents, fetch_hadith_collection, get_category_links
import re
from tqdm import tqdm

documents = []
links, book_titles = fetch_hadith_collection('https://hadithcollection.com/sahihbukhari')
for link, (book_title, total_pages) in tqdm(zip(links, book_titles), desc='Outer loop'):
    for page in tqdm(range(1, total_pages + 1), desc="Inner loop"):
        urls = get_category_links(f"{link}/page/{page}")
        for url in urls:
            content, title = get_contents(url)
            documents.append(Document(page_content=content, metadata={"title": title, "url": url, "category": book_title}))



print(len(documents))


with open("dataset.txt", 'w', encoding="utf8") as file:
    for doc in documents:
        num = doc.metadata['title'].split('Number')[1]
        number = re.findall(r'\d+', num)[0]
        file.write(f"{int(number)}\n{doc.metadata['title']}\n{doc.metadata['category']}\n{doc.metadata['url']}\n{doc.page_content}\n\n\n")