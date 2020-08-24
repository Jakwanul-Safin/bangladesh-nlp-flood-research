# Bangladesh NLP Flood Research
Code repository for Bangladesh NLP Flood Research Project

## Article Scraping
Scraping articles using serpAPI. Get articles distribution, site distribution and other information about articles.

### Data
Get data using `./get_articles_data.sh`. paper_data folder will be downloaded.
* paper_data - Download using `./get_articles_data.sh`. Contains article text, datePublished and other information. 1 folder per newspaper
    * [newspaper-name] - Each newspaper has a folder, which contains the following files:
        * [newspaper-name]1_sites.json = File containing sites for queries. This file is made by the file serpAPI.py
        * [newspaper-name]1_data.json = File containing data extracted from the sites noted in the _sites.json files.
    * all_paper_data - Contains data extracted for all newspapers.

### Folders
* article_scrapes - Folder containing scraping methods for different newspapers. These methods are called in all_papers.py in method `scrape_main`


### Important Files
* paper_index.json - Contains information about:
    * Paper name
    * Number of sites for that paper
    * Date Range for which sites have been collected for the paper
<br/><span style="color:red">Note: paper_index contains paper names recognized by the different functions used in all_papers. Hence, check this file in order to reference a paper_name</span>
* all_papers.py - Main file for scraping data. Important functions are:
    * `count_sites_all_paper` = Counts the total number of sites in all scraped papers.
    * `get_date_range` = Counts date ranges for which data has been scraped, given a newspaper
    * `get_last_date` = Gets the last date for which data has been scraped, given a newspaper
    * `scrape_main` = Main scraping function, once a json of sites has been made using serpAPI. Add the scraper function for the particular newspaper (located in article_scrapes) to this method.
    * `make_id_filename` = Get id of text, given filename downloaded from tagtog
    * `make_newspaper_filename` = Get newspaper name of text, given filename downloaded from tagtog
    * `get_id_data` = Get specific data, given id. Option to query all data or a certain part (like datePublished, or text etc...)
    * `site_distribution` = Gets a graph of site distribution. Data saved in site_distribution.json. Figure saved in site_distribution.png
    * `scraped_data_distribution` = Gets a graph of scraped data distribution. Data saved in scraped_data_distribution.json. Figure saved in scraped_data_distribution.png
* serpAPI.py - serpAPI scraping code. Main functions:
    * `SERP` = queries serpAPI given start year, end year, query, site and paper name. Makes a folder to called [paper_name] and stores queried sites in [paper_name]1_sites.json
