from unidecode import unidecode
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

def theDailyStarScrape(soup, meta):
    headline = soup.find('h1', itemprop='headline')
    if headline: headline = headline.text
    authors = soup.find('div', itemprop='author')
    if authors:
        authors2 = authors.find('span', itemprop='name')
        if authors2:
            authors3 = authors.find_all('a')
            if authors3:
                authors = [a.text for a in authors3]
            else:
                authors = authors.text
    text = soup.find('article', role='article')
    if text:
        textp = text.find_all('p')
        if textp: text = ' '.join([p.text for p in textp])

    if not text: text = ''
    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'authors': authors,
        'text': 'Date Published:{}      \n'.format(meta['datePublished']) + text
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
    site = 'https://www.thedailystar.net/bangladesh-national-election-2018/news/bnp-gives-5-seats-ldp-1670998'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site)
    print(theDailyStarScrape(soup, meta))
