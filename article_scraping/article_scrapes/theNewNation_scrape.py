from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import json
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

def theNewNationScrape(soup, meta):
    # print(soup)
    # main_div = soup.find('div')
    # print(main_div.find('article'))
    # print(main_div.find('article').get_text())

    headline, text = None, ''
    headline = soup.find('h1', id='newsheader')
    if headline: headline = headline.text.strip()
    textmain = soup.find('div', class_='news_text')
    if textmain:
        textp = textmain.find_all('p')
        if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])
    if not text:
        textmain = soup.find_all('div', align='justify')
        if textmain:
            text = ' '.join([p.text for p in textmain])

    datePublished = soup.find('time', class_='dateline')
    if datePublished:
        datePublished = datePublished.getText()
        datePublished = datePublished.split('/')[0].strip()
    if datePublished: datePublished = str(parse_date(datePublished))

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'datePublished': datePublished,
        'text': 'Date Published:{}      \n'.format(datePublished or meta['datePublished'])+text
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
    site = 'http://m.thedailynewnation.com/news/131551/rain-submerges-parts-of-ctg.html'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site)
    print(theNewNationScrape(soup, meta))
