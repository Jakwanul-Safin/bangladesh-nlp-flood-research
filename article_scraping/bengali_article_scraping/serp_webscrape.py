"""
Adpated from the SERP API scraper for English articles made by Tejit Pabari. 
This scraper attempts to get links to as many Bengali newspapers as possible.

Changes:
The number of newspapers has been increased from 10 to 17 and the query has 
changed to a single OR query of several Bengali terms. There were also changes
to various options for the search which made it more ammenable for Bengali.

Need serpAPI key for this. Send an email to tvp2107@columbia.edu for the key
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta, date

from serpapi import GoogleSearch

root_folder = 'data/serp'
SERPAPI_KEY = "d9093b222729e12bc1e16c9c3f9e49f6b01714952eefa889a51c2acbdbe2fda9"

# Logger for full SERP Queries
queryLogger = logging.getLogger('SERP Queries')
queryLogger.setLevel(logging.INFO)
ch = RotatingFileHandler("log/serpQuery.log", maxBytes=40000, backupCount=1000, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
ch.setFormatter(formatter)
queryLogger.addHandler(ch)

# Logger for basic output
logger = logging.getLogger("SERP Logger")
logger.setLevel(logging.DEBUG)
sth = logging.StreamHandler()
ch = logging.handlers.RotatingFileHandler("log/serpScrape.log", maxBytes=40000)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(sth)


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
                "the_azadi": "https://dainikazadi.net",
                "daily_sangram": "https://dailysangram.com",
                "sangbad_pratidin": "https://www.sangbadpratidin.in"
            }

"""
Get google news results from serpAPI
Need serpAPI key for this. Send an email to tvp2107@columbia.edu for the key
"""
def make_params(query: str, site: str, date_start: str = '1/1/2020',
                date_end: str = '1/1/2021', num_results: int = 100, paper: str = 'theDailyStar',
                search_news = True):
    """
    Makes a parameter dict to pass to serpAPI
    :param query: query to search in google news
    :param site: site root url (eg. www.google.com)
    :param date_start: Starting date for search in format MM/DD/YYYY
    :param date_end: Ending date for search in format MM/DD/YYYY
    :param num_results: Number of results per page (between 1-100)
    :param paper: paper name
    :return: query dict for query information, param dict to pass to serpAPI
    """
    query_r = {
        'query': query,
        'paper': paper,
        'searchnws': search_news,
        'date_range': [date_start, date_end] if date_start!=date_end else date_start
    }
    params = {
        "engine": "google",
        "q": "{} site:{}".format(query, site),
        "google_domain": "google.com",
        "gl": "bd",
        "hl": "bn",
        'filter':'0',
        "num": num_results,
        "api_key": SERPAPI_KEY
    }
    
    if date_start is not None and date_end is not None:    
        params["tbs"] = "cdr:1,cd_min:{},cd_max:{}".format(date_start, date_end)
            
    if search_news:
        params["tbm"] = "nws"
    return query_r, params

def range_dates(date_start:date, date_end:date, increment:timedelta):
    """
    Helper function to get time intervals
    :param date_start: Starting date
    :param date_end: ending date
    :param increment: increments dates by value
    :return: list of dates
    """
    while date_start + increment < date_end:
        yield date_start, date_start + increment
        date_start += increment
    yield date_start, date_end

def query_SERP(query:str, site:str, dates:list=[(None, None)], num_results:int=100, 
               paper_name:str=None, search_news:bool=False,
               seen_sites_file:str=None, LIMIT_COUNT:int = 10000) -> list:
    """
    Make dict for serp query using make_params()
    query serpAPI
    :param query: query string for google news
    :param site: site root url (eg. www.google.com)
    :param dates: list of dates
    :param num_results: number of results
    :param paper_name: name of paper
    :param LIMIT_COUNT: limits number of pages that can be loaded
    :return: Full results query with the query info saved - list of query dicts containing query information and sites list for the query
    """
    seen_sites = set()
    if seen_sites_file:
        with open(seen_sites_file, 'r') as f:
            seen_sites = set(json.load(f))
    
    overlap = 0
    results = {}
<<<<<<< HEAD
=======
    priorCount = 0
>>>>>>> decc4f05f788897bd000116e12db1a50840c7526
    for d in dates:
        try:
            # Get query dict and params dict
            query_r, params = make_params(query=query, site=site, date_start=d[0], date_end=d[1],
                                          num_results=num_results, paper=paper_name, search_news=search_news)

            count = 0
<<<<<<< HEAD
            priorCount = 0
=======
>>>>>>> decc4f05f788897bd000116e12db1a50840c7526
            # Loop through till end of search results or error encountered
            while LIMIT_COUNT > 0:
                LIMIT_COUNT -= 1
                
                # serpAPI query
                params['start'] = count
                count += num_results
                
                queryLogger.info(params)
                client = GoogleSearch(params)
                search_results = client.get_dict()
                if 'error' in search_results:
                    if search_results['error'] != "Google hasn't returned any results for this query.":
                        logger.warning("Found error {}".format(search_results['error']))
                    break

                if search_news:
                    news_results = search_results['news_results']
                else:
                    news_results = search_results['organic_results']

                if news_results is None or len(news_results) == 0:
                    break
                
                for news in news_results:
                    link = news['link']
                    if link in results:
                        overlap += 1
                        continue

                    if link in seen_sites:
                        continue
                    
                    info = {k:v for k, v in news.items() if k in ('title', 'link', 'date')}
                    results[link] = info
                
            logger.debug('Date Range: {}-{}\tTotal Sites: {}'.format(d[0],d[1], len(results)-priorCount))
            priorCount = len(results)

        except Exception as e:
            logger.exception("Exception: {} Date:{}".format(e, d))
            print(search_results)
            raise
            
    logger.debug('Total Sites: {}, Overlap: {}'.format(len(results), overlap))
    return list(results.values())

def default_search_dates():
    """The default time intervals used in the search"""
    start = date(1996, 1, 1)
    end = date(2009, 12, 31)
    increment = timedelta(days=2*365)
    date1980_2009 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

    start = date(2010, 1, 1)
    end = date(2021, 12, 31)
    increment = timedelta(days=90)
    date2010_2021 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

    dates = date1980_2009+date2010_2021
    return dates

def run(query = "জলমগ্ন OR জোয়ারের OR প্লাবিত OR বন্যা", dates = default_search_dates()):
    for paper_name, site in names_site.items():
        logger.info("Scrapping {} articles from {}".format(paper_name, site))
        outfile = "data/{}_serp_{}_webscrape.json".format(paper_name, query.replace(" ", "_"))
        if os.path.exists(outfile):
            logger.exception("File {} already exists".format(outfile))
            raise FileExistsError
        queryRes = query_SERP(query, site, dates=dates) 
        with open(outfile, 'w') as f:
            json.dump(queryRes, f)

if __name__ == "__main__":
    run(query="")
