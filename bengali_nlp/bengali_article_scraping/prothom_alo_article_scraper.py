import sys, os
from bs4 import BeautifulSoup

import time
import json, re

import logging
from logging.handlers import RotatingFileHandler
from datetime import date
import requests

from basicBanglaTools import translateBengaliDate

# Logger for Scrapping
logger = logging.getLogger('Scraping Prothom Alo Articles')
logger.setLevel(logging.DEBUG)
rh = RotatingFileHandler(os.path.join(os.path.dirname(sys.argv[0]), 'log/prothom_alo_scrape_log.log'), maxBytes=40000, backupCount=100, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rh.setFormatter(formatter)
logger.addHandler(rh)

sh = logging.StreamHandler()
logger.addHandler(sh)


def extractAllUniqueLinks():
    uniqueLinks = {}
    fileformat = re.compile("prothom_alo_webscrapes_[^.]*\.json")
    for filename in os.listdir(os.path.join(os.path.dirname(sys.argv[0]), 'data')):
        if not fileformat.match(filename):
            continue

        with open(os.path.join(os.path.dirname(sys.argv[0]), 'data', filename), 'r', encoding="utf-8") as f:
            res = json.load(f)
            logger.info("{} articles found in {}".format(len(res), filename))
            for r in res:
                uniqueLinks[r['link']] = r
    logger.info("{} unique links collected".format(len(uniqueLinks)))
    return uniqueLinks

def extractCategorizationFromLink(link):
    f = link.split('/')[:-1]
    i = max(i for i, v in enumerate(f) if ".com" in v)
    return f[i+1:]

def scrapeProthomaloFromSearchInfo(info):
    res = {k:v for k, v in info.items()}
    res['category'] = extractCategorizationFromLink(info['link'])
    res['paper'] = 'Prothom Alo'
    res['language'] = 'Bengali'
    
    res['date'] = translateBengaliDate(res['date'])
    
    page = requests.get(info['link'])
    soup = BeautifulSoup(page.content.decode('utf-8','ignore'), features="html.parser")
    
    headline, text = None, ''
    headline = soup.find('h1', class_='headline')
    if headline: headline = headline.text.strip()
    textmain = soup.find('div', class_='story-content')
    textp = textmain.find_all('p')
    if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])
    
    res['headline'] = headline
    res['content'] = text
    
    return res

def scrapeFromLinks(links, delay = 0.5):
    article_scrapes = []
    for i, r in enumerate(links):
        time.sleep(delay)
        try:
            scrapedArticle = scrapeProthomaloFromSearchInfo(r)
        except AttributeError as e:
            logger.exception("Could not scape {} with exception {}".format(r, e))
            continue
        article_scrapes.append(scrapedArticle)

        if (i % 50) == 0:
            logger.info("{}/{} articles scraped".format(i, len(links)))
    
    logger.info("All {} articles scraped".format(len(article_scrapes)))
    return article_scrapes

if __name__ == "__main__":
    allLinks = extractAllUniqueLinks().values()
    article_scrapes = scrapeFromLinks(allLinks)

    outpath='data/prothom_alo_articlescrapes_bengali.json'
    outfile = os.path.join(os.path.dirname(sys.argv[0]), outpath)
    if os.path.exists(outfile):
        logger.warning("File {} Already Exists!".format(outfile))
        raise FileExistsError

    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(article_scrapes, f)