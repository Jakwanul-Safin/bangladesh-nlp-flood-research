from unidecode import unidecode
from bs4 import BeautifulSoup
import requests

def bdnewsScrape(soup, meta):
    # print(soup)
    # main_div = soup.find('div')
    # print(main_div.find('article'))
    # print(main_div.find('article').get_text())

    headline, text = None, ''
    headline = soup.find('h1', class_='print-only')
    if headline: headline = headline.text.strip()
    textmain = soup.find('div', class_='wrappingContent')
    textp = textmain.find_all('p')
    # print(textp)
    if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'text': 'Date Published:{}      \n'.format(meta['datePublished'])+text
    }

if __name__=='__main__':
    site = 'https://bdnews24.com/bangladesh/2014/11/01/massive-blackout-brings-bangladesh-to-its-knees'
    meta = {'datePublished':'TRIAL'}
    page = requests.get(site)
    # print(page.text)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(bdnewsScrape(soup, meta))
