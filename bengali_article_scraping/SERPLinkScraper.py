import os, sys, time
from datetime import timedelta, date, datetime

import csv
import pandas as pd

import logging
from logging.handlers import RotatingFileHandler

from serpapi import GoogleSearch

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
ch = logging.handlers.RotatingFileHandler("log/serpScrape.log", maxBytes=400000, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
    
class SERPError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        
class SERPLinkScraper:
    def __init__(self, config):
        self.config = config
        self.search_delay = 3.601 # Delay to avoid hiting the 1000 queries per hour limit
        self.last_search = - self.search_delay

    def search_results_for(self, params):
        results = {}

        # Loop through till end of search results or error encountered
        MAX_HITS = int(1e10)
        for start in range(0, MAX_HITS, self.config.num()):
            params['start'] = start

            time.sleep(max(0, self.search_delay + self.last_search - time.time()))

            queryLogger.info(params)
            client = GoogleSearch(params)
            search_results = client.get_dict()


            self.last_search = time.time()

            if 'error' in search_results:
                if "Google hasn't returned any results for this query" in search_results['error']:
                    return results
                elif "Your searches for the month are exhausted" in search_results['error']:
                    raise SERPError(f"SERP searches exhausted\n{search_results['error']}")
                else:
                    raise SERPError(f"Found SERP error:\n{search_results['error']}")

            news_results = search_results['news_results'] if self.config.searchnews() else search_results['organic_results']
            

            if news_results is None or not news_results:
                return results

            for news in news_results:
                link = news['link']
                if link in results:
                    continue
                
                info = {k:v for k, v in news.items() if k in ('title', 'link', 'date')}
                results[link] = info
        raise OverflowError(f"Excepted at most {MAX_HITS} results for each query")

    
    def execute_search(self, params):
        try:
            news_results = self.search_results_for(params)
        except SERPError as e:
            logger.warning(f"Issue with SERP {e}")
            raise e
        
        for result in news_results.values():
            yield result
        
    def run(self):
        columnnames = ('title', 'paper', 'date', 'link', 'query', 'search_date_start', 'search_date_end')
        outfile = self.config.outfile()
        if os.path.exists(outfile):
            logger.warning(f"An output File {outfile} Already Exists!")
            mode = 'a+'
            self.seen_links = set(pd.read_csv(outfile, delimiter = "\t")['link'])
        else:
            mode = 'w'
            self.seen_links = set()
            
        executed_searches, found_links = self.config.completed_searches(), set()
        total_searches = sum(1 for _ in self.config.searches())
        
        start = time.time()
        with open(outfile, mode, newline = '', encoding="utf-8") as f:
            writer = csv.DictWriter(f, delimiter = "\t", fieldnames = columnnames)
            
            if mode == 'w':
                writer.writeheader()
            
            q_links = 0
            for i, search in enumerate(self.config.searches()):
                query, paper, date, params = search
                if (query, paper, date) in executed_searches:
                    continue

                q_new_links = 0
                try:
                    for result in self.execute_search(params):
                        if result['link'] in found_links:
                            continue
                        else:
                            q_new_links += 1
                            q_links += 1
                            found_links.add(result['link'])
                        
                        result['query'] = query
                        result['paper'] = paper
                        result['search_date_start'], result['search_date_end'] = date
                        writer.writerow({k:(v.replace("\t", "    ") if k != 'category' else v) for k, v in result.items()})
                except Exception as e:
                    self.config.store_completed_searches(executed_searches)
                    raise e
                
                executed_searches.add((query, paper, date))
                    
                logger.debug(f'Total New Sites from {query} on {paper} in {date[0]}-{date[1]}: {q_new_links}')
                
                if i % 50 == 0:
                    logger.info(f"Executed {i}/{total_searches} searches in {timedelta(seconds = time.time() - start)}\nTotal Sites: {q_links}")
                    
        logger.info(f"Completed in {timedelta(seconds = time.time() - start)}")