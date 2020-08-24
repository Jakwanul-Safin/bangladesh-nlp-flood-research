from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import json

def prothomaloScrape(soup, meta):
    # print(soup)
    # main_div = soup.find('div')
    # print(main_div.find('article'))
    # print(main_div.find('article').get_text())

    headline, text = None, ''
    headline = soup.find('h1', class_='headline')
    if headline: headline = headline.text.strip()
    textmain = soup.find('div', class_='story-content')
    textp = textmain.find_all('p')
    if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])

    script = soup.find_all('script')
    datePublished = None
    for s in script:
        try:
            scriptjs = json.loads(s.string)
            datePublishedStrings = ['datePublished', 'datepublished', 'datepublish', 'datePublish', 'publishdate', 'publishDate',
                                    'publisheddate', 'publishedDate']
            for st in datePublishedStrings:
                if st in scriptjs:
                    datePublished = scriptjs[st]
                    break
        except:
            continue

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'text': 'Date Published:{}      \n'.format(meta['datePublished'])+text,
        'datePublished': datePublished
    }

def get_soup(site, selenium=False):
    if selenium:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path='/Applications/chromedriver', options=options)
        driver.get(site)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        open('trial.html','w').write(driver.page_source)
    else:
        page = requests.get(site)
        soup = BeautifulSoup(page.text, 'html.parser')
    return soup

if __name__=='__main__':
    site = 'https://en.prothomalo.com/environment/Natural-disasters-in-Himalaya-to-affect-Bangladesh'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site, True)
    print(prothomaloScrape(soup, meta))
