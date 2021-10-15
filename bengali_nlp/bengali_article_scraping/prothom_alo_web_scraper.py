"""Scraper for the Prothom Alo website. Can successfully scrape topic and search pages as
of 6/3/2021."""

import sys, os
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
import time

import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import date

# Path to Chromedriver
CHROMEDRIVER_PATH = "C:/Users/aweso/Desktop/chromedriver.exe"
if CHROMEDRIVER_PATH is None:
    raise ValueError("Replace CHROMEDRIVER_PATH the appropriate path to your Chomedriver")

options = webdriver.ChromeOptions()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
options.add_argument("--headless")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# Logger for Queries
logger = logging.getLogger('Scraping Prothom Alo Queries')
logger.setLevel(logging.DEBUG)
rh = RotatingFileHandler(os.path.join(os.path.dirname(sys.argv[0]), 'log/prothom_alo_scrape_log.log'), maxBytes=40000, backupCount=100)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rh.setFormatter(formatter)
logger.addHandler(rh)


def selectDate(driver, selectedDate, delay = 0.5):
    """Selects date on a datepicker"""

    time.sleep(delay)
    elem = driver.find_element_by_css_selector('select.react-datepicker__year-select')
    elem.click()

    time.sleep(delay)
    elem = driver.find_element_by_xpath("//*[contains(text(), '{:%Y}')]".format(selectedDate))
    elem.click()

    time.sleep(delay)
    elem = driver.find_element_by_css_selector('select.react-datepicker__month-select')
    elem.click()

    time.sleep(delay)
    elem = driver.find_element_by_xpath("//*[contains(text(), '{:%B}')]".format(selectedDate))
    elem.click()

    time.sleep(delay)
    elem = driver.find_element_by_css_selector('div.react-datepicker__day--0{:%d}'.format(selectedDate))
    elem.click()

def setDateRange(driver, startDate = None, endDate = None, delay = 0.5):
    """Sets the date range on a search page"""

    if startDate is not None or endDate is not None:
        time.sleep(delay)
        elem = driver.find_element_by_xpath("//*[contains(text(), 'তারিখ')]")
        elem.click()

        time.sleep(delay)
        start_date_picker, end_date_picker = driver.find_elements_by_css_selector('div.react-datepicker__input-container')

    if startDate is not None:
        time.sleep(delay)
        start_date_picker.click()
        selectDate(driver, startDate)
    
    if endDate is not None:
        time.sleep(delay)
        end_date_picker.click()
        selectDate(driver, endDate)

def qArticlesOnSearchPage(driver, delay = 0.5):
    """Returns the number of articles found on search page"""
    time.sleep(delay)
    elem = driver.find_elements_by_xpath('//*[@id="container"]/div/div[2]/div[1]/div[1]/div[1]/span[2]')[0]
    return elem.text

def loadUntilEnd(driver, limit = 80000, failTolerance = 20, delay = 1.1):
    """Continually clicks the load more button the prothom alo site if it exists. 
        Returns the html page content of the final page.
        @param limit: the maximum number of times load is clicked
        @param failTolerance: number of failures to click button before terminating
        @param delay: delay between load more clicks to keep from being walled out
            by server
    """

    loadClicks, fails = 0, 0
    for _ in range(limit):
        page = driver.page_source
        if fails >= failTolerance:
            break

        time.sleep(delay)
        try:
            elem = driver.find_element_by_css_selector('span.load-more-content')
        except NoSuchElementException:
            logger.info("Reached End of Document")
            break

        #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        driver.execute_script("arguments[0].scrollIntoView();", elem)
        
        try:
            elem.click()
            loadClicks += 1
            fails = 0
            logger.debug("Loaded new articles {} times".format(loadClicks))
        except ElementClickInterceptedException:
            logger.warning("Click to load more intercepted")
            fails += 1
        except StaleElementReferenceException:
            logger.warning("Load more button is stale")
            fails += 1
    
    return page

def getResultsFromWebpage(soup):
    """Extracts Article links and metadata from the soup. Returns data in the form
        [{title: [TITLE], date: [DATE], link: [ARTICLE_URL]},...]
    """
    matches = []
    stories = (hl.parent.parent for hl in soup.find_all("h2", attrs={"class":"headline"}))
    
    for div in stories:
        match = {}
        match["title"] = div.find(attrs={"class":"headline"}).text.strip()
        
        hrefs = div.find_all('a', href=True)
        if len(hrefs) != 1:
            raise Exception("{} hrefs found, expected 1".format(len(hrefs)))
        match['link'] = hrefs[0]["href"]
        
        timestamps = div.find_all('time')
        if len(timestamps) != 1:
            raise Exception("{} timestamps found, expected 1".format(len(timestamps)))
        match['date'] = timestamps[0].text
        
        matches.append(match)
    
    return matches

def run(link, output, startDate = None, endDate = None, limit=80000, pageOutput = None, OVERWRITE = False, REQUIRE_CONFIRMATION=True):
    """ Runs the full scrapping operation. Results in the writing of scraped links to output file.
        The output is formated as
            [{title: [TITLE], date: [DATE], link: [ARTICLE_URL]},...]

        @param link: URL of search or topic page in Prothom Alo
        @param output: relative path to the ouput destination of results
        @param startDate: start date of search (only applies to searches)
        @param endDate: end date of search (only applies to searches)
        @param limit: limit of the number of new loads clicked in scrape
        @param pageOutput: relative path to store raw html of page
        @param OVERWRITE: whether to overwrite current contents of output file
        @param REQUIRE_CONFIRMATION: whether to have a [y:n] confirmation to begin the scrape
    """

    outfile = os.path.join(os.path.dirname(sys.argv[0]), output)
    if os.path.exists(outfile) and not OVERWRITE:
        logger.warning("Output file already exists {}".format(limit))
        raise FileExistsError

    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
    driver.get(link)

    if "search?" in link:
        # Checks to see is this is a search page in prothom alo
        setDateRange(driver, startDate, endDate)
        #qHits = qArticlesOnSearchPage(driver)
        #logger.debug("Expect {} articles".format(qHits))

    logger.debug("Running {} Limit".format(limit))
    
    if REQUIRE_CONFIRMATION:
        response = None
        while response not in ['y', 'n']:
            response = input("Begin Scrape from {} into {} with a {} load limit? [y:n]?".format(link, outfile, limit)).lower()
        
        if response=='n':
            driver.close()
            sys.exit()
    
    page = loadUntilEnd(driver, limit = limit)
    if pageOutput is not None:
        pageOutpath=os.path.join(os.path.dirname(sys.argv[0]), pageOutput)
        with open(pageOutpath, 'w', encoding='UTF-8', errors='strict', buffering=1) as f:
            f.write(page)

    soup = BeautifulSoup(page, 'html.parser')
    res = getResultsFromWebpage(soup)

    logger.debug("Scraped {} article links".format(len(res)))
    with open(outfile, "w") as f:
        json.dump(res, f)

    driver.close()


if __name__ == "__main__":
    startDate = date(2009, 1, 1)
    endDate = date.today()

    logger.info("Start of Scrape")
    run(link = "https://www.prothomalo.com/search?q=প্লাবিত", 
        output = "data/prothom_alo_seachপ্লাবিত.json", 
        limit=3, 
        OVERWRITE = True,
        REQUIRE_CONFIRMATION = False,
        pageOutput=os.path.join(os.path.dirname(sys.argv[0]), 'log/prothom_alo_searchপ্লাবিত.html')
    )
    logger.info("End of Scrape")
