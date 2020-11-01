from unidecode import unidecode
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
from uuid import uuid4
import time

def dailyStarArchiveLinks(soup):
    links = soup.findAll('a', href=re.compile(r'[0-9]{4}/[0-9]{2}/[0-9]{2}'))
    links2 = []
    for i,l in enumerate(links):
        href = l['href']
        if 'http://archive.thedailystar.net/magazine/' not in href: href = 'http://archive.thedailystar.net/magazine/' + href
        innerSoup = get_soup(href)
        table = innerSoup.find('table')
        try:
            innerTable = table.findAll('table')[4]
        except:
            innerTable = soup.findAll('table')[4]
        td = innerTable.findAll('td')[0]
        innerLinks = td.findAll('a')
        innerHrefs = [l2['href'] for l2 in innerLinks]
        href2 = [href.replace('index.htm',h) for h in innerHrefs]
        links2.extend(href2)
        if i==10: print('.',end='')
    print()
    return links2

def theDailyStarScrape(soup, site):
    datePublished = None
    matches = re.search(r'\d{4}/\d{2}/\d{2}', site)
    if matches: datePublished = matches[0].replace('/', '-')
    meta = {
        "link": site,
        "query_info": {
            "query": "dailyStarArchive",
            "paper": "theDailyStar",
            "date_range": []
        },
        'datePublished': datePublished
    }
    try:
        table = soup.find('table')
        try:
            innerTable = table.findAll('table')[4]
        except:
            innerTable = soup.findAll('table')[4]
        td = innerTable.findAll('td')[1]
        ps = []
        headline, author = '', ''
        for i,f in enumerate(td.findAll('p')):
            if i==0: continue
            elif i==1: headline = f.text
            elif i==2: author = f.text
            else: ps.append(f.text)
        article = {
            'headline': unidecode(headline),
            'authors': unidecode(author),
            'text': "Date Published:{}      \n".format(datePublished) + unidecode("".join(ps))
        }
        id = str(uuid4())
        return {
            'meta': meta,
            'article': article,
            'id': id
        }
    except Exception as e:
        print('\n',e,site,'\n')
        return None


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
    site = 'http://archive.thedailystar.net/campus/campusarchive.htm'
    soup = get_soup(site)
    links = dailyStarArchiveLinks(soup)
    print('All Links',len(links))
    data = []
    for i,site in enumerate(links):
        soup = get_soup(site)
        resp = theDailyStarScrape(soup, site)
        if resp: data.append(resp)
        if i%100 == 0:
            print('.',end = '')
            json.dump(data, open('../paper_data/thedailystar/theDailyStar2_data.json', 'w'), indent=2)
            time.sleep(10)


    json.dump(data, open('../paper_data/thedailystar/theDailyStar2_data.json','w'), indent=2)