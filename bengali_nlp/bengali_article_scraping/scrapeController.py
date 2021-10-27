import os
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import logging

import csv
from urllib.error import HTTPError

from scraper import *

logger = logging.getLogger('Scraping Links')
logger.setLevel(logging.DEBUG)

PAPER_SCRAPER = {
    "prothom_alo": ProthomAloScraper(),
    "kaler_kantho": KalerKanthoScraper()
}

class ScrapeController:
    """"Controllers for handling scraping text from news websites. Each website requires an individual
        scraper to handle its naunces.
    """

    def __init__(self, links: List[Dict[str, Any]], output_file: str, 
                 skip_articles: Optional[set] = None, 
                 skipped_links_output_file = None, 
                 OVERWRITE = False, APPEND = True,
                 paper_scrappers = PAPER_SCRAPER,
                 delay = 1
                ):
        """" 
        @param links - [{'link': <URL>, 'paper': <paper-name>, (optionally has 'title': <title>)}]
        @param output_file - file where all links will be outputed
        """
        
        self.links = {paper: links for paper, links in links.groupby('paper')}

        self.output_file = output_file
        self.scrapers = PAPER_SCRAPER
        self.skip_articles = skip_articles if skip_articles is not None else set()
        self.skipped_articles = defaultdict(list)
        self.delay = delay
                
        self.column_names = ('title', 'paper', 'date', 'link', 'headline', 'content', 'category', 'language')
        if os.path.exists(output_file) and not OVERWRITE:
            logger.warning("An output File {} Already Exists!".format(output_file))
            self.skip_articles |= set(pd.read_csv(output_file, delimiter = "\t")['link'])
        else:
            with open(output_file, 'w', newline='', encoding="utf-8") as fullArticleFile:
                writer = csv.DictWriter(fullArticleFile, delimiter = "\t", fieldnames = self.column_names)
                writer.writeheader()
        
    def scrape(self, scrapeLinks):
        total = sum(len(links) for links in scrapeLinks.values())
        toScrape = {paper: (time.time(), len(links)-1 ) for paper, links in scrapeLinks.items()}
        
        for _ in range(total):
            if not toScrape:
                return 

            # Chooses next paper to scrape based on the last access to the article
            # Among the papers whose last access was greater than the delay it chooses the paper
            # that has the most articles to scrape
            # If no such paper exits, it chooses the last accessed one
            paper = max(toScrape.keys(), key= lambda paper: (min(time.time() - toScrape[paper][0], self.delay), toScrape[paper][1]) )

            lastAccess, index = toScrape[paper]
            if time.time() - lastAccess < self.delay:
                time.sleep(max(self.delay - time.time() + lastAccess, 0))

            link = scrapeLinks[paper][index]
            if index != 0:
                toScrape[paper] = (time.time(), index - 1)
            else:
                del toScrape[paper]
                
            try:
                scrape = self.scrapers[paper].scrape(link)
                if scrape["content"] is None or scrape["headline"] is None:
                    self.skipped_articles[paper].append(link)
                else:
                    yield scrape
            except HTTPError as e:
                logger.exception(f"HTTP Error {e}\n{link} could not be scrapped")
            except Exception as e:
                logger.exception(f"{e}\n{link} could not be scrapped")
                self.skipped_articles[paper].append(link)
                continue
        
    def run(self):
        start = time.time()
        with open(self.output_file, 'a+', newline='', encoding="utf-8") as fullArticleFile:
            writer = csv.DictWriter(fullArticleFile, delimiter = "\t", fieldnames = self.column_names)
            
            totalArticles = sum(len(links) for _, links in self.links.items())
            logger.info(f"Found {totalArticles} links")
            
            unavailable_papers = ", ".join(
                paper 
                for paper in self.links.keys() 
                if paper not in self.scrapers
            )
            logger.info(f"Scrapper unavailable for {unavailable_papers}")

            scrapeLinks = {
                paper: 
                [
                    link 
                        for _, link in links.iterrows()
                        if link['link'] not in self.skip_articles 
                            and self.scrapers[paper].filter_url(link['link'])
                ] 
                for paper, links in self.links.items()
                if  paper in self.scrapers
            }
            totalArticles = sum(len(links) for links in scrapeLinks.values())
            logger.info(f"Will Scape {totalArticles} articles")
            
            for i, scrape in enumerate(self.scrape(scrapeLinks)):
                if i % 20 == 0:
                    current = timedelta(seconds = round(time.time()-start, 2))
                    eta = totalArticles/i * current if i != 0 else 0
                    
                    scraped = i-sum(len(links) for _, links in self.skipped_articles.items())
                    scrape_rate = (100 * scraped/i) if i != 0 else 0
                    
                    logger.info(f"Completed {i}/{totalArticles} articles\tScraped {scraped}({scrape_rate:.2f}%)\tTime: {current}, ETA: {eta}")
                print(i, scrape)
                writer.writerow({k:(v.replace("\t", "    ") if k != 'category' else v) for k, v in scrape.items() if k in self.column_names})
        logger.info(f"Completed in {timedelta(seconds = time.time() - start)}")
    
    def df(self):
        return pd.read_csv(self.output_file, delimiter = "\t")
    
    def save_skipped(self, file):
        self.skipped_links = pd.DataFrame([{'paper':paper, 'title':info['title'], 'link': info['link']} for paper, links in ctrl.skipped_articles.items() for info in links])
        self.skipped_links.to_csv(file)
        
    def load_skipped(self, file):
        self.skipped_links.read_csv(file, index_col=0)