import requests 
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from helper_utilities import get_contents

r = requests.get('https://hadithcollection.com/category/sahihbukhari/sahih-bukhari-book-01-revelation')
soup = BeautifulSoup(r.content, 'html.parser')
documents = []
for a in soup.find_all('a', class_="entry-button"):
    content, parent_link, parent_title, title = get_contents(a['href'])


    doc = Document(
        page_content=content,
        metadata={
            "parent_url": parent_link,
            "source_url": a['href'],
            "author": "Hadith Collection",
            "title": title,
            "language": "Arabic",
            "length": len(content),
            "format": "text/plain",
        }
    )
    documents.append(doc)
    
print(len(documents))