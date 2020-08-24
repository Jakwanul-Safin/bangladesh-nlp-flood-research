from unidecode import unidecode
from bs4 import BeautifulSoup
import requests

def dailySunScrape(soup, meta):
    # print(soup)
    # main_div = soup.find('div')
    # print(main_div.find('article'))
    # print(main_div.find('article').get_text())

    headline = soup.find('h2', class_='news-headline')
    if headline: headline = headline.text.strip()
    # authors = main_div.find('div', class_='author-bg')
    # if authors: authors = authors.text.strip()
    authors = None
    text = None
    textp = soup.find_all('p')
    if textp: text = ' '.join([p.text for p in textp])
    if not text: text=''
    else: text = text.lower().split('editor')[0]

    if headline: headline = unidecode(headline)
    if authors: authors = unidecode(authors)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'authors': authors,
        'text': 'Date Published:{}      \n'.format(meta['datePublished'])+text
    }

if __name__=='__main__':
    site = 'https://www.daily-sun.com/post/419686/Irregularities-at-DGHS:-TK-85500-spent-to-buy-book-of-TK-5500'
    meta = {'datePublished':'TRIAL'}
    page = requests.get(site)
    # print(page.text)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(dailySunScrape(soup, meta))
