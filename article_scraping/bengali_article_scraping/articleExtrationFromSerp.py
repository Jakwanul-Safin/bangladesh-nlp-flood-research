import sys, os
import time

import logging
from logging.handlers import RotatingFileHandler
from datetime import date, timedelta

import json, csv, re, requests

from bs4 import BeautifulSoup
import numpy as np

from fake_useragent import UserAgent
import urllib

from basicBanglaTools import *

# {"the_azadi": "https://dainikazadi.net"} was removed since the site did not appear to have accessible urls

names_site = {  "prothom_alo": "https://www.prothomalo.com",
                "the_daily_janakantha":"https://www.dailyjanakantha.com",
                "kaler_kantho": "https://www.kalerkantho.com", 
                "the_daily_jugantor": "https://www.jugantor.com",
                "the_daily_ittefaq": "https://www.ittefaq.com.bd",
                "samakal": "https://samakal.com",
                "amader_shomoy": "http://www.dainikamadershomoy.com",
                "bhorer_kagoj": "https://www.bhorerkagoj.com",
                "daily_manab_zamin": "https://mzamin.com",
                "alokito_bangladesh": "https://www.alokitobangladesh.com",
                "the_sangbad": "http://sangbad.net.bd",
                "the_daily_inqilab": "https://www.dailyinqilab.com",
                "jaijaidin": "https://www.jaijaidinbd.com",
                "daily_naya_diganta": "https://www.dailynayadiganta.com",
                "daily_sangram": "https://dailysangram.com",
                "sangbad_pratidin": "https://www.sangbadpratidin.in"
            }

# Logger for Scrapping
logger = logging.getLogger('Scraping From SERP Links Articles')
logger.setLevel(logging.DEBUG)
rh = RotatingFileHandler(os.path.join(os.path.dirname(sys.argv[0]), 'log/articles_from_SERP_links_scrape_log.log'), maxBytes=40000, backupCount=100, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rh.setFormatter(formatter)
logger.addHandler(rh)

#sh = logging.StreamHandler()
#logger.addHandler(sh)

def linksFromSERPSearch(papername):
    filename = "data/{}_serp_জলমগ্ন_OR_জোয়ারের_OR_প্লাবিত_OR_বন্যা_webscrape.json".format(papername)
    if not os.path.exists(filename):
        logger.warning("Attempt to find links from {} failed\n{} does not exist".format(papername, filename))
        raise FileNotFoundError
    with open(filename, 'r') as f:
        res = json.load(f)
    return res

bengaliTextChars = set(' ৫এঊ্টধহ‘৯ি১ঠূ০’আ৮ডইতঞণঐশ৭২ঙ৬।াড়ছলঢ়যঃরৌোংউষদগব.ঢঈসচঝঅীথজখও ()়;,কঘেয়ঋমঔুভফনপঁ৩ৎ৪ৈ!–ৃ-')

def textFilter(txt, thres = 0.95):
    #extraneousChars = "".join(set(c for c in txt if c not in bengaliTextChars))
    #if extraneousChars:
    #    print(extraneousChars)
    return len(txt) > 5 and sum(1 for c in txt if c in bengaliTextChars)/len(txt) > thres

def requestWithUA(url):
    ua = UserAgent()
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': ua.random
        }
    )
    page = urllib.request.urlopen(request)
    soup = BeautifulSoup(page, "html.parser")
    
    return soup

def cleanNewlining(text):
    return "\n".join(block.strip() for block in text.replace("\r", " ").split("\n") if block.strip())

scrapingParams = {
    "prothom_alo":{
        'headline': lambda soup: soup.find('title').text.replace("| প্রথম আলো", "").strip(),
        'content': lambda soup: "\n".join(elt.text for elt in soup.find_all("div", class_=["bn-story-element", "story-element-image-title"]) if elt.text)
    },
    "the_daily_janakantha": {
        'headline': lambda soup: soup.find("title").text.replace("দৈনিক জনকন্ঠ || ", ""), 
        'content': lambda soup: cleanNewlining(soup.find('div', class_='article-details').text)
    },
    "kaler_kantho": {
        'headline': lambda soup: soup.find('title').text.split("|")[0].strip(), 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="some-class-name2").text)
    },
    "the_daily_jugantor": {
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="news-element-text").text),
        'image_captions': lambda soup: cleanNewlining("\n".join(caption.text for caption in soup.find_all('figcaption', class_="pb-2")))
    },
    "the_daily_ittefaq": {
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="dtl_content_block").text)
    },
    "samakal": {
        'requestBy': lambda url: requestWithUA(url),
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="description").text)
    },
    'amader_shomoy': {
        'headline': lambda soup: soup.find('title').text.replace("\x96", "").replace("Dainik Amader Shomoy", "").strip(), 
        'content': lambda soup: cleanNewlining('\n'.join(ptag.text for ptag in soup.find_all('p') if textFilter(ptag.text)))
    },
    'bhorer_kagoj': {
        'headline': lambda soup: soup.find('h2', class_ = "title").text.strip(),
        "content": lambda soup: cleanNewlining(soup.find('div', {"id":"content-p"}).text)
    },
    "daily_manab_zamin": {
        'headline': lambda soup: soup.find('title').text.strip(),
        "content": lambda soup: cleanNewlining(soup.find('div', class_ = ["dtext", "details-text"]).text)
    },
    "alokito_bangladesh": {
        'headline': lambda soup: soup.find('title').text.strip(),
        "content": lambda soup: cleanNewlining(soup.find('div', class_ = "dtl_content_block").text)
    },
    "the_sangbad": {
        'headline': lambda soup: soup.find('div', class_ = 'news-title').text.strip(),
        "content": lambda soup: cleanNewlining(soup.find('div', class_ = "fullnews").text)
    },
    "the_daily_inqilab": {
        'requestBy': lambda url: requestWithUA(url),
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', {"id": "ar_news_content"}).text)
    },
    "jaijaidin": {
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="dtl_content_block").text)
    },
    "daily_naya_diganta": {
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="news-content").text)
    },
    "daily_sangram": {
        'headline': lambda soup: soup.find('title').text, 
        'content': lambda soup: cleanNewlining(soup.find('div', class_="postBody").text)
    },
    "sangbad_pratidin": {
        'headline': lambda soup: soup.find('h1').text.strip(), 
        'content': lambda soup: cleanNewlining("\n".join(para.text for para in soup.find('div', class_='sp-single-post').find_all("p") if textFilter(para.text, thres=0.8)))
    }
}

def SCRAPE_FROM_LINK(paper, link, content_thres = 200):
    if 'requestBy' not in scrapingParams[paper]:
        page = requests.get(link['link'])
        soup = BeautifulSoup(page.content.decode('utf-8','ignore'), features="html.parser")
    else:
        soup = scrapingParams[paper]['requestBy'](link['link'])
    
    if any('crossorigin' in script.attrs for script in soup.find_all("script")):
        logger.warning("Cross Orgin detected")
        soup = requestWithUA(link['link'])
    
    try:
        headline = scrapingParams[paper]['headline'](soup)
        content = scrapingParams[paper]['content'](soup)
    except AttributeError:
        logger.warning("Content from {} at {} didn't get scraped".format(paper, link))
        return None, None
    
    if len(content) < content_thres:
        logger.warning("Content from {} at {} too short, didn't get scraped".format(paper, link))
        return None, None
    
    if textFilter(content, thres=0.80):
        return headline, content

    return None, None

def extractCategorizationFromLink(link):
    f = link.split('/')[:-1]
    i = max(i for i, v in enumerate(f) if "." in v)
    return f[i+1:]

def SCRAPE_FROM_SERP_SEARCH_INFO(papername, info):
    res = {k:v for k, v in info.items()}
    res['category'] = extractCategorizationFromLink(info['link'])
    res['paper'] = papername
    res['language'] = 'Bengali'

        
    headline, content = SCRAPE_FROM_LINK(papername, info)
    
    res['headline'] = headline
    res['content'] = content
    
    return res

def run(delay = 1):
    allLinks = {paper: linksFromSERPSearch(paper) for paper in names_site.keys()}

    badUrl = re.compile(".+\/\?pg=\d+$")
    allLinks["the_daily_ittefaq"] = [entry for entry in allLinks["the_daily_ittefaq"] if not badUrl.match(entry["link"])]

    totalArticles = sum(len(v) for v in allLinks.values())
    logger.info("Found {} articles".format(totalArticles))

    toScrape = {paper: (time.time(), len(links)-1 ) for paper, links in allLinks.items()}
    logger.info("Will Scape {} articles".format(sum(ind+1 for _, ind in toScrape.values())))

    for _ in range(totalArticles):
        if not toScrape:
            break

        # Chooses next paper to scrape based on the last access to the article
        # Among the papers whose last access was greater than the delay it chooses the paper
        # that has the most articles to scrape
        # If no such paper exits, it chooses the last accessed one
        papername = max(toScrape.keys(), key= lambda paper: (min(time.time() - toScrape[paper][0], delay), toScrape[paper][1]) )

        lastAccess, index = toScrape[papername]
        if time.time() - lastAccess < delay:
            time.sleep(max(delay - time.time() + lastAccess, 0))

        link = allLinks[papername][index]
        try:
            if index != 0:
                toScrape[papername] = (time.time(), index - 1)
            else:
                del toScrape[papername]

            yield SCRAPE_FROM_SERP_SEARCH_INFO(papername, link)
        except Exception as e:
            logger.exception(f"{e}\n{link} could not be scrapped")
            #raise e


if __name__ == "__main__":
    columnnames = ('title', 'paper', 'date', 'link', 'headline', 'content', 'category', 'language')
    
    outpath='data/serpAllFullArticlesScrape.csv'
    outfile = os.path.join(os.path.dirname(sys.argv[0]), outpath)
    if os.path.exists(outfile):
        logger.warning("Output File {} Already Exists!".format(outfile))
        raise FileExistsError


    start = time.time()
    with open(outfile, 'w', newline='', encoding="utf-8") as fullArticleFile:
        writer = csv.DictWriter(fullArticleFile, delimiter = "\t", fieldnames = columnnames)

        writer.writeheader()
        skipped = 0
        for i, scrape in enumerate(run()):
            if i % 20 == 0:
                logger.info(f"Scraped {i-skipped}/{i} articles in {timedelta(seconds = round(time.time()-start, 2))}")

            if scrape["content"] is None or scrape["headline"] is None:
                skipped += 1
                continue
            writer.writerow({k:(v.replace("\t", "    ") if k != 'category' else v) for k, v in scrape.items()})
    logger.info(f"Completed in {timedelta(seconds = time.time() - start)}")