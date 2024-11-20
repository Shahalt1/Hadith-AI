import requests 
from bs4 import BeautifulSoup
from re import findall
from math import ceil
from typing import List, Tuple, Optional
from langchain_core.documents import Document


def get_contents(url: str) -> Tuple[Optional[str], str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('article', class_="post")
    title = article.find('h1', class_="page-title").get_text()
    content_div = article.find('div', class_="entry-content")
    Ad_div = content_div.find('div', class_="code-block")
    content = ''
    try:
        content_tags = Ad_div.find_next_siblings('p')
        for tag in content_tags:
            content += tag.get_text() + '\n'
            
    except AttributeError:
        print("No content found in div -> p")
        content = None  # Set content to None if not found
        
    if len(content) < 15:
        content = ''
        
    if not content:
        try:
            content = Ad_div.find_next_sibling('div').get_text()
        except AttributeError:
            print("No content found in div -> div")
            content = None  # Set content to None if not found

    if content is None:
        print("No content found in div")

    return content, title


def fetch_hadith_collection(url: str) -> Tuple[List[str], List[Tuple[str, int]]]:
    """
    Fetches links and book titles with page counts from the given Hadith collection URL.
    
    Args:
        url (str): URL of the Hadith collection page.
    
    Returns:
        Tuple[List[str], List[Tuple[str, int]]]: A tuple containing a list of links and 
        a list of book titles with their respective page counts.
    """
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article', class_='page')
        if not article:
            raise ValueError("No 'article' tag found on the page with class 'page'")
        
        categories = article.find('div', class_="entry-content")
        if not categories:
            raise ValueError("No 'div' with class 'entry-content' found in the article")
        
        # Initialize result containers
        links = []
        book_titles = []
        pattern = r'\[(\d+)\]'
        
        # Extract links and book titles
        for header in categories.find_all('h3'):
            link = header.find('a')
            book_title = header.get_text()
            title, n = book_title.split('\xa0')
            
            # Extract the number of pages and calculate total pages
            pages = findall(pattern=pattern, string=n)
            if not pages:
                raise ValueError(f"No pages found for book title: {book_title}")
            
            total_pages = ceil(int(pages[0]) / 15)
            links.append(link['href'])
            book_titles.append((title, total_pages))
        
        return links, book_titles
    
    except requests.RequestException as e:
        raise ConnectionError(f"An error occurred while making the HTTP request: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

def get_category_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try: 
        entries_div = soup.find('div', class_="entries")
        anchors = entries_div.find_all('a', class_="entry-button")
        links = [anchor['href'] for anchor in anchors]
    except Exception as e:
        print(f"An error occurred while fetching category links: {e}")
        links = []
    return links



def load_documents(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf8') as file:
        return [
            Document(
                page_content="\n".join(lines[4:]),
                metadata={"number": lines[0], "title": lines[1], "category": lines[2], "url": lines[3]}
            )
            for lines in (doc.split("\n") for doc in file.read().split("\n\n"))
            if lines[0] or len(lines) >= 4
        ]