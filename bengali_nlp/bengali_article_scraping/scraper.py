from abc import ABC, abstractclassmethod
from collections import defaultdict

import sys
sys.path.insert(0, '..')

import pandas as pd
import re

from fake_useragent import UserAgent
import requests
import urllib

from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup

import logging

from basicBanglaTools import *

logger = logging.getLogger('Scraping Links')
logger.setLevel(logging.DEBUG)

bengaliTextChars = set(' ৫এঊ্টধহ‘৯ি১ঠূ০’আ৮ডইতঞণঐশ৭২ঙ৬।াড়ছলঢ়যঃরৌোংউষদগব.ঢঈসচঝঅীথজখও ()়;,কঘেয়ঋমঔুভফনপঁ৩ৎ৪ৈ!–ৃ-')

def textFilter(txt, thres = 0.95):
    return len(txt) > 5 and sum(1 for c in txt if c in bengaliTextChars)/len(txt) > thres

def cleanNewlining(text):
    return "\n".join(block.strip() for block in text.replace("\r", " ").split("\n") if block.strip())

class Scraper(ABC):
    @abstractclassmethod
    def headline(self, soup):
        raise NotImplementedError
    
    @abstractclassmethod
    def date(self, soup):
        raise NotImplementedError
    
    @abstractclassmethod
    def content(self, soup):
        raise NotImplementedError
        
    @abstractclassmethod
    def paper(self):
        raise NotImplementedError
        
    def filter_url(self, url):
        """True if URL could be a positive article and false if not"""
        return True
    
    def scrape(self, info):
        res = {k:v for k, v in info.items()}
        res['paper'] = self.paper()
        res['language'] = 'Bengali'

        headline, date, content = self.text_from_link(info['link'])
        res['category'] = self.categories(info['link'])

        res['headline'] = headline
        res['date'] = date
        res['content'] = content

        return res
    
    def categories(self, link):
        f = link.split('/')[:-1]
        i = max(i for i, v in enumerate(f) if "." in v)
        return f[i+1:]
    
    def request(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content.decode('utf-8','ignore'), features="html.parser")
        return soup
    
    def requestWithUA(self, url):
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

    def text_from_link(self, link):
        try:
            soup = self.request(link)
            text = self.text_from_soup(soup, link)
        except AttributeError:
            try:
                soup = self.requestWithUA(link)
                text = self.text_from_soup(soup, link)
            except AttributeError:
                logger.warning("Content from {} at {} didn't get scraped; could not exctract content from webpage".format(self.paper(), link))
                return None, None, None
            
        return text
    
    def length_filer(self, content, content_thres  = 200):
        # Filters for text length and page content
        if len(content) < content_thres:
            return False
        if not textFilter(content, thres=0.80):
            return False 
        return True
    
    def text_from_soup(self, soup, link):
        # Extracting data from page source
        try:
            headline, content, date = self.headline(soup), self.content(soup), self.date(soup)
        except AttributeError as e:
            raise e
            
        if not self.length_filer(content):
            logger.warning("Content from {} at {} too short, didn't get scraped".format(self.paper(), link))
            return None, None, None

        return headline, date, content

class ProthomAloScraper(Scraper):
    def __init__(self):
        self.AMP = False
    
    def paper(self):
        return "prothom_alo"
        
    def headline(self, soup, AMP = False):
        if AMP or self.AMP:
            soup.find('h1', class_='story-headline').text
        return soup.find('title').text.replace("| প্রথম আলো", "").strip()
    
    def content(self, soup, AMP = False):
        if AMP or self.AMP :
            return "\n".join(div.text for div in soup.find_all('div', class_ = "story-element-text"))
        return "\n".join(elt.text for elt in soup.find_all("div", class_=["bn-story-element", "story-element-image-title"]) if elt.text)
        
    def date(self, soup, AMP = False):
        if AMP or self.AMP:
            date_raw = soup.find('time', class_='published-time').text
            return str(datetime.strptime(re.search("\s*([^,]*, \d+)", date_raw)[1], "%B %d, %Y"))
        
        date_raw = soup.find('div', class_='storyPageMetaData-m__publish-time__19bdV').time.span.text 
        return str(translateBengaliDate(re.search(": ([^,]*),", date_raw)[1]))
    
    def filter_url(self, url):
        if url == 'https://www.prothomalo.com/':
            return False
        return not any(tag in url for tag in ("/topic/", "/video/", "/author/", '/feature/', '/poll/'))
    
    def text_from_link(self, link):
        if "/amp/" in link:
            self.AMP = True
            text = super().text_from_link(link)
            self.AMP = False
            return text
            
        return super().text_from_link(link)
    
class KalerKanthoScraper(Scraper):
    def paper(self):
        return "kaler_kantho"
    
    def headline(self, soup):
        return soup.find('title').text.split("|")[0].strip()
    
    def content(self, soup):
        return cleanNewlining(soup.find('div', class_="some-class-name2").text)
    
    def date(self, soup):
        return translateBengaliDate(re.search("[০১২৩৪৫৬৭৮৯]+ [^,]*, [০১২৩৪৫৬৭৮৯]+", " ".join(tag.text for tag in soup.find_all('p', class_='n_author')))[0])
    
    def filter_url(self, url):
        return all(section.isdigit() for section in url.split("/")[-4:])

class BDNewsScraper(Scraper):
    pass

class SamakalScraper(Scraper):
    def paper(self):
        return "samakal"
    
    def headline(self, soup):
        return soup.find('title').text
    
    def content(self, soup):
        return cleanNewlining(soup.find('div', class_="description").text)
    
    def date(self, soup):
        return soup

class DailyJuganatorScraper(Scraper):
    def paper(self):
        return "the_daily_jugantor"
    
    def headline(self, soup):
        return soup.find('title').text

    def date(self, soup):
        return soup
    
    def content(self, soup):
        return cleanNewlining(soup.find('div', class_="news-element-text").text)

    def image_captions(self, soup):
        return cleanNewlining("\n".join(caption.text for caption in soup.find_all('figcaption', class_="pb-2")))

class ManabZaminScraper(Scraper):
    def paper(self):
        return "daily_manab_zamin"
    
    def headline(self, soup):
        return soup.find('title').text.strip()

    def date(self, soup):
        return soup
    
    def content(self, soup):
        return cleanNewlining(soup.find('div', class_ = ["dtext", "details-text"]).text)

class InqilabScraper(Scraper):
    def paper(self):
        return "the_daily_inqilab"

    def headline(self, soup):
        return soup.find('title').text
    
    def date(self, soup):
        return soup

    def content(self, soup):
        return cleanNewlining(soup.find('div', {"id": "ar_news_content"}).text)

class NayaDigantaScraper(Scraper):
    def paper(self):
        return "daily_naya_diganta"

    def headline(self, soup):
        return soup.find('title').text

    def date(self, soup):
        return soup

    def content(self, soup):
        return cleanNewlining(soup.find('div', class_="news-content").text)

class BhorerKagojScraper(Scraper):
    def paper(self):
        return "bhorer_kagoj"
    
    def headline(self, soup):
        return soup.find('h2', class_ = "title").text.strip()
    
    def date(self, soup):
        return soup
    
    def content(self, soup):
        return cleanNewlining(soup.find('div', {"id":"content-p"}).text)

class SangbadPratidinScraper(Scraper):
    def paper(self):
        return "sangbad_pratidin"

    def headline(self, soup):
        return soup.find('h1').text.strip()

    def date(self, soup):
        return soup

    def content(self, soup):
        return cleanNewlining("\n".join(para.text for para in soup.find('div', class_='sp-single-post').find_all("p") if textFilter(para.text, thres=0.8)))

class IttefeqScraper(Scraper):
    def paper(self):
        return "the_daily_ittefaq"

    def headline(self, soup):
        return soup.find('title').text

    def date(self, soup):
        return soup

    def content(self, soup):
        return cleanNewlining(soup.find('div', class_="dtl_content_block").text)

class AmaderShomoy(Scraper):
    def paper(self):
        return "amader_shomoy"
    
    def headline(self, soup):
        return soup.find('title').text.replace("\x96", "").replace("Dainik Amader Shomoy", "").strip()
    
    def date(self, soup):
        return soup

    def content(self, soup):
        return cleanNewlining('\n'.join(ptag.text for ptag in soup.find_all('p') if textFilter(ptag.text)))