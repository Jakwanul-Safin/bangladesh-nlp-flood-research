from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from datetime import datetime
from datefinder import find_dates

def parse_date(date_obj):
    if not date_obj: return None
    elif type(date_obj)==datetime:
        return date_obj
    else:
        dates = [f for f in find_dates(date_obj)]
        if dates: return dates[0]
    return None

def theIndependentScrape(soup, meta):
    headline, text = None, ''
    headline = soup.find('div', id='hl2')
    if headline: headline = headline.text.strip()

    textmain = soup.find('div', id='newsDtl')
    textp = textmain.find_all('p')
    if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])

    datePublished = soup.find('span', id='news_update_time')
    if datePublished:
        datePublished = datePublished.getText()
        datePublished = datePublished.split('/')[0].strip()
    if datePublished: datePublished = str(parse_date(datePublished))

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'datePublished': datePublished,
        'text': 'Date Published:{}      \n'.format(datePublished or meta['datePublished'])+text,

    }

def get_soup(site, selenium=False):
    if selenium:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path='/Applications/chromedriver', options=options)
        driver.get(site)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # open('trial.html','w').write(driver.page_source)
    else:
        page = requests.get(site)
        soup = BeautifulSoup(page.text, 'html.parser')
    return soup

if __name__=='__main__':
    site = 'http://www.theindependentbd.com/post/48397'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site)
    print(theIndependentScrape(soup, meta))
