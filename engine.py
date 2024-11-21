import requests 
from bs4 import BeautifulSoup
# from langchain_core.documents import Document
# from helper_utilities import get_contents, fetch_hadith_collection, get_category_links
import re
from tqdm import tqdm
from chromadb import PersistentClient # v4.0.0
import pandas as pd


def get_hadith_collection(url):
    documents = []
    links, book_titles = fetch_hadith_collection(url)
    for link, (book_title, total_pages) in tqdm(zip(links, book_titles), desc='Outer loop'):
        for page in tqdm(range(1, total_pages + 1), desc="Inner loop"):
            urls = get_category_links(f"{link}/page/{page}")
            for url in urls:
                content, title = get_contents(url)
                documents.append(Document(page_content=content, metadata={"title": title, "url": url, "category": book_title}))




def create_dataset(documents):
    with open("dataset.txt", 'w', encoding="utf8") as file:
        for doc in documents:
            num = doc.metadata['title'].split('Number')[1]
            number = re.findall(r'\d+', num)[0]
            file.write(f"{int(number)}\n{doc.metadata['title']}\n{doc.metadata['category']}\n{doc.metadata['url']}\n{doc.page_content}\n\n\n")
            
import pandas as pd
def create_csv_from_documents(documents, filename="output.csv"):
    """Creates a CSV file from a list of Langchain Documents."""

    data = []
    for doc in documents:
        row = {
            "page_content": doc.page_content,
            **doc.metadata
        }
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    
# documents =  get_hadith_collection('https://hadithcollection.com/sahihbukhari')
# create_dataset(documents)
# create_csv_from_documents(documents)

df = pd.read_csv('output.csv')
df.reset_index(inplace=True)

client = PersistentClient("vectordb", )
# client.delete_collection(name="hadith-collection")
collection = client.get_or_create_collection("hadith-collection", metadata={"hnsw:space": "cosine"})


def upsert_data(df):
    for _, row in df.iterrows():
        collection.upsert(
            ids=[str(row['index'])],
            documents=[row['page_content']],
            metadatas=[
                {"Title": row['title'], "Category": row['category'], "URL": row['url']}
            ]
        )

upsert_data(df)