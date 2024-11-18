import requests 
from bs4 import BeautifulSoup

def get_contents(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('h1', class_="page-title").get_text()
    parent_link = soup.find('a', class_="ct-term-3")['href']
    parent_title = soup.find('a', class_="ct-term-3").get_text()
    content_divs = soup.find_all('div', class_='entry-content')
    content = content_divs[2].find_all('div')[1].get_text()
    # print(f"{title}\n{parent_link}\n{parent_title}\n{content}")
    
    return content, parent_link, parent_title, title