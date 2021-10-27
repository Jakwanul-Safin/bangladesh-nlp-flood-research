The purpose of this directory is to allow for easy scraping of news articles from specific site. There are two main components to this process. First is obtaining links to webpages for news articles and second is scraping it's contents.

------------------------------------------------------------------
OBTAINING LINKS TO NEWS ARTICLES OF RELEVANCE
-----------------------------------------------------------------

The first step is accomplished here by the SERP API (with uses search engines, namely Google, to generate results to specific). The output for this step will be a tsv, csv or JSON file of the following form

    [{'title': [ARTICLE_1_TITLE], 'paper': [ARTICLE_1_PAPER], 'link': [ARTICLE_1_URL], ... } ...]

In json form, tt is a list of dictionaries representing the link to a given article with additional metadata. Only the paper name and url is strictly necesary for the next step. Likewise, for the other formats it will be a csv with the appropriate columns.

To obtain this JSON file following the steps:
    1) Create a YAML file with the configurations for the search in the configs folder
    2) Run "python LinkScrape.py [CONFIG_FILENAME]"
This will output a tsv with the required headers.

Notes and Tips:
    1) Make to you have a working SERP acount with searches. The auth token must be placed in the config file
    2) To see what which queries are being done what the results are check the serpQuery and serpScrap logs
    3) Certain searches will retrieve better results, i.e. using quotes around words will turn the search into a exact match query which may be helpful in certain contexts
    4) Be mindful of the number of searches a config uses since it may quickly exhaust an account. Having many choices of dates with many choices of newspapers with many keywords combinations will lead to a cubic growth in the number of searches. For less popular websites it's often better to use larger date rangers. Smaller date ranges however, may yeild more articles.

------------------------------------------------------------------
EXTRACTING TEXT CONTENT FROM OBTAINED LINKS
-----------------------------------------------------------------

This stage involves extracting the text form the new paper articles. Since news sites are ever changing and inconsistent a different scraper has to be written for each site and may periodically go out of date. In order, to add or renew support for a given paper see the "scraper.py" file and add classes to it. Then go to the scrapeController.py file and register those classes with the appropriate newspaper.

To run the available scrapes run the following:

    python ArticleScrape.py [PATH_TO_LINKS_FILE] [PATH_TO_OUTPUT_FILE]

The output will be a tsv with the various columns including:
    1) title - title of the article
    2) content - content of the news article
    3) date - date scrapped with the article
    4) link - link to the article