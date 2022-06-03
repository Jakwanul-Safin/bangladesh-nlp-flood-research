"""
Adpated from the SERP API scraper for English articles made by Tejit Pabari. 
This scraper attempts to get links to as many Bengali newspapers as possible.

Changes:
The number of newspapers has been increased from 10 to 17 and the query has 
changed to a single OR query of several Bengali terms. There were also changes
to various options for the search which made it more ammenable for Bengali.

Need serpAPI key for this. Send an email to tvp2107@columbia.edu for the key
"""

import os, sys, time
import json, yaml
from datetime import timedelta, date, datetime

import logging
from logging.handlers import RotatingFileHandler

from serpapi import GoogleSearch

root_folder = 'data/serp'
SERPAPI_KEY = [KEY]

# Logger for full SERP Queries
queryLogger = logging.getLogger('SERP Queries')
queryLogger.setLevel(logging.INFO)
ch = RotatingFileHandler("log/serpQuery.log", maxBytes=400000, backupCount=1000, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
ch.setFormatter(formatter)
queryLogger.addHandler(ch)

# Logger for basic output
logger = logging.getLogger("SERP Logger")
logger.setLevel(logging.DEBUG)
#sth = logging.StreamHandler()
ch = logging.handlers.RotatingFileHandler("log/serpScrape.log", maxBytes=400000, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
#logger.addHandler(sth)


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
                "sangbad_pratidin": "https://www.sangbadpratidin.in",
                "the_daily_star": "https://www.thedailystar.net/bangla",
                "bd_news": "bangla.bdnews24.com"
            }
""""“The Daily Star,” “BD News,” “Daily Observer,” “Daily Sun,” “Dhaka Tribune,” “New Age,” “Prothomalo,” “The Independent,” “The New Nation”"""

class SERPError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class SERPWebscraper:
    def __init__(self, config_file = None):
        if config_file is not None:
            self.load_config(config_file)
        self.config = {
            "searchnws": False, 
            "gl": "bd", 
            "hl": "bn", 
            "filter": "0", 
            "num": 100,
            "output_dir": "",
            "output_file": "serp_{paper}_{query}.json",
            "quote_sub": "[QUOTE]",
            "overwrite": False,
            "skip_existing": True,
            "seen_sites_file": None
            }
        self.search_delay = 3.601 # Delay to avoid hiting the 1000 queries per hour limit
        self.last_search = - self.search_delay

    def load_config(self, config_file):
        with open(config_file, "r", encoding='utf-8') as f:
            self.config.update(yaml.load(f, Loader=yaml.FullLoader))

    def check_config(self):
        missing = [param for param in ("queries", "papers", "date_ranges", 'SERPAPI_KEY') if param not in self.config]
        if len(missing) > 0:
            raise KeyError("Config missing: {}".format(", ".join(missing)))
        
        unknown_papers = [paper not in names_site for paper in self.config["papers"]]
        if len(missing) > 0:
            raise KeyError("Unknown papers: {}\nPlease add to paper list".format(", ".join(unknown_papers)))

        self.generate_dates()
    
    def range_dates(self, date_start:date, date_end:date, increment:timedelta):
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

    def generate_dates(self):
        self.dates = []
        for start, end, inc in self.config["date_ranges"]:
            start = datetime.strptime(start, "%m/%d/%Y").date()
            end = datetime.strptime(end, "%m/%d/%Y").date()
            inc = timedelta(days=inc)
            self.dates.extend((s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s, t in self.range_dates(start, end, inc))
        return self.dates
    
    def outfile_for(self, paper, query):
        filename = self.config["output_file"].format(paper = paper, query = query.replace(" ", "_").replace("\"", self.config['quote_sub']))
        return os.path.join(self.config["output_dir"], filename)

    def search_results_for(self, params):
        results = {}

        # Loop through till end of search results or error encountered
        MAX_HITS = int(1e10)
        for start in range(0, MAX_HITS, self.config['num']):
            params['start'] = start

            time.sleep(max(0, self.search_delay + self.last_search - time.time()))

            queryLogger.info(params)
            client = GoogleSearch(params)
            search_results = client.get_dict()
            search_results = {'error': "Google hasn't returned any results for this query"}


            self.last_search = time.time()

            if 'error' in search_results:
                if "Google hasn't returned any results for this query" in search_results['error']:
                    return results
                elif "Your searches for the month are exhausted" in search_results['error']:
                    raise SERPError(f"SERP searches exhausted\n{search_results['error']}")
                else:
                    raise SERPError(f"Found SERP error:\n{search_results['error']}")

            news_results = search_results['news_results'] if self.config['searchnws'] else search_results['organic_results']
            
            if news_results is None or news_results:
                return results

            for news in news_results:
                link = news['link']
                if link in results:
                    self.overlap += 1
                    continue

                if link in self.seen_sites:
                    continue
                
                info = {k:v for k, v in news.items() if k in ('title', 'link', 'date')}
                results[link] = info
        raise OverflowError(f"Excepted at most {MAX_HITS} results for each query")

    def query_SERP(self, query:str, site:str, dates:list=[(None, None)]) -> list:
        """
        Make dict for serp query using make_params()
        query serpAPI
        :param query: query string for google news
        :param site: site root url (eg. www.google.com)
        :param dates: list of dates

        :return: List of results in format [{'title':[TITLE], 'link':[LINK], 'date':[DATE]}]: (date according to SERP)
        """
        self.seen_sites = set()
        if self.config["seen_sites_file"] is not None:
            with open(self.config["seen_sites_file"], 'r') as f:
                self.seen_sites = set(json.load(f))
        
        overlap = 0
        results = {}
        for start_date, end_date in dates:
            params = {
                "engine": "google",
                "q": "{} site:{}".format(query, site),
                "google_domain": "google.com",
                "gl": self.config['gl'],
                "hl": self.config['hl'],
                'filter':self.config['filter'],
                "num": self.config['num'],
                "api_key": self.config['SERPAPI_KEY'],
                "tbs": "cdr:1,cd_min:{},cd_max:{}".format(start_date, end_date)
            }
                        
            if self.config['searchnws']:
                params["tbm"] = "nws"

            try:
                new_results = self.search_results_for(params)
            except SERPError as e:
                logger.warning(f"Issue with SERP {e}")
                raise e
            results.update(new_results)
            logger.debug(f'Date Range: {start_date}-{end_date}\tSites Found: {len(new_results)}\tTotal Found: {len(results)}')

        logger.debug('Total Sites: {}, Overlap: {}'.format(len(results), overlap))
        return list(results.values())

    def run(self):
        self.check_config()

        for paper, query in ((p, q) for q in self.config["queries"] for p in self.config["papers"]):
            site = names_site[paper]
            logger.info(f"Scrapping {paper} articles from {site} for {query}")

            outfile = self.outfile_for(paper, query)

            if os.path.exists(outfile):
                logger.exception("File {} already exists".format(outfile))
                if not self.overwrite:
                    raise FileExistsError
                if self.skip_existing:
                    continue
            
            dates = self.generate_dates()
            queryRes = self.query_SERP(query, site, dates) 
            with open(outfile, 'w') as f:
                json.dump(queryRes, f)

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
    priorCount = 0
    start = time.time() - 2
    for d in dates:
        try:
            # Get query dict and params dict
            query_r, params = make_params(query=query, site=site, date_start=d[0], date_end=d[1],
                                          num_results=num_results, paper=paper_name, search_news=search_news)

            count = 0
            # Loop through till end of search results or error encountered
            while LIMIT_COUNT > 0:
                LIMIT_COUNT -= 1
                
                # timer to prevent reaching hour cap
                time.sleep(max(0, 3.601 + start - time.time()))
                start = time.time()

                # serpAPI query
                params['start'] = count
                count += num_results
                
                queryLogger.info(params)
                client = GoogleSearch(params)
                search_results = client.get_dict()
                if 'error' in search_results:
                    if search_results['error'] != "Google hasn't returned any results for this query.":
                        logger.warning("Found error {}".format(search_results['error']))
                        
                    if 'You are exceeding 1,000 searches per hour.' in search_results:
                        time.sleep(3600)
                        queryLogger.info(params)
                        client = GoogleSearch(params)
                        search_results = client.get_dict()
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

def range_dates(start, end, increment):
    return []

def default_search_dates(setting = 1):
    """The default time intervals used in the search
            setting = 0  used until 7/2/21
                has more fine grained dates
            setting = 1 used from 7/2/21
                has corser (10) date ranges to minimize searches
    """
    if setting == 0:
        start = date(1996, 1, 1)
        end = date(2009, 12, 31)
        increment = timedelta(days=4*365)
        date1980_2009 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        start = date(2010, 1, 1)
        end = date(2021, 12, 31)
        increment = timedelta(days=420)
        date2010_2021 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        dates = date1980_2009+date2010_2021
    elif setting == 1:
        start = date(1996, 1, 1)
        end = date(2013, 12, 31)
        increment = timedelta(days=10*365)
        date1980_2009 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        start = date(2013, 1, 1)
        end = date(2021, 12, 31)
        increment = timedelta(days=420)
        date2010_2021 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        dates = date1980_2009+date2010_2021
    elif setting == 2:
        start = date(1996, 1, 1)
        end = date(2015, 12, 31)
        increment = timedelta(days=5*365)
        date1980_2009 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        start = date(2016, 1, 1)
        end = date(2021, 12, 31)
        increment = timedelta(days=50)
        date2010_2021 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        dates = date1980_2009+date2010_2021
    elif setting == 3:
        start = date(1996, 1, 1)
        end = date(2012, 12, 31)
        increment = timedelta(days=5*365)
        date1980_2009 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        start = date(2013, 1, 1)
        end = date(2021, 12, 31)
        increment = timedelta(days=15)
        date2010_2021 = [(s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s,t in range_dates(start, end, increment)]

        dates = date1980_2009+date2010_2021
    return dates

def run(query = "জলমগ্ন OR জোয়ারের OR প্লাবিত OR বন্যা", dates = default_search_dates(), higher_sample = {}, dates2 = None):
    for paper_name, site in names_site.items():
        logger.info(f"Scrapping {paper_name} articles from {site} for {query}")
        outfile = "data/{}_serp_{}_webscrape.json".format(paper_name, query.replace(" ", "_")).replace("\"", "[RVDQUOTE]")
        if os.path.exists(outfile):
            logger.exception("File {} already exists".format(outfile))
            continue
            raise FileExistsError
        queryRes = query_SERP(query, site, dates=dates if paper_name not in higher_sample else dates2) 
        with open(outfile, 'w') as f:
            json.dump(queryRes, f)

keywords = {"জলমগ্ন": "submerged",
    "জোয়ারের":"tidal", 
    "প্লাবিত": "flooded", 
    "বন্যা": "flood", 
    "জলাবদ্ধ": "waterlogged", 
    "উজান": "upstream", 
    "ঘূর্ণিঝড়": "cyclone",
    "নদী": "river", 
    "ভাঙ্গন": "erosion",
    "বাঁধ": "embankment",
    "বেড়িবাঁধ": "embankment",
    "পোল্ডার": "polder"
}

updatedKeywords = {
    "বেড়িবাঁধ ক্ষতিগ্রস্ত": "embankment damaged",
    "বেড়িবাঁধ উপচে": "Water overflew the embankment",
    "মানুষ পানিবন্দী": "people are waterlogged",
    "নিমজ্জিত হয়েছে": "are submerged",
    "পানিবন্দি হয়ে পড়েছে": "have become waterlogged",
    "প্রবল বর্ষণ": "heavy rain",
    "টানা বৃষ্টি": "continuous rain",
    "পাহাড়ি ঢলে": "steam coming down the hill"
}

commonBanglaWords = {
    "হয়েছে": "Done",
    "এক": "One",
    "হয়ে": "Become",
    "যায়": "Goes",
    "দিয়ে": "With",
    "সময়": "Time",
    "কথা": "Talk",
    "রয়েছে": "There are",
    "টাকা": "Money",
    "হিসেবে": "As",
    "বছর": "Years",
    "দেশের": "Of the country"
}
queried  = []

# Quote character replaced with [QUOTE] for flood related keywords
# Quote character replaced with [RQUOTE] for random keywords

config_file = "article_scraping/bengali_article_scraping/RandomDenseSERPSearch.yaml"
if __name__ == "__main__":
    if len(sys.argv) == 2:
        webscraper = SERPWebscraper()
        webscraper.load_config(sys.argv[1])
        webscraper.run()
#    for keyword in ("হয়েছে", "এক"):#commonBanglaWords.keys(): #| updatedKeywords.keys():
#        searchTerm = f"\"{keyword}\""
#        run(query = searchTerm, dates = default_search_dates(2), 
#                higher_sample = set(["prothom_alo", "kaler_kantho", "samakal", "bd_news"]), 
#                dates2 = default_search_dates(3)
#            )
