Welcome to the IRI Bangla NLP Flood project. There are a variety of tools and components here aimed at tackling the problem of detecting and localizing floods in Bangladesh. Our solution involves the aggregating of large amounts of bengali news media and using NLP tools to determine the frequency of flooding, as well as the time and location of these floods.

While these tools were made for a particular project they may be useful for others. The main workflow for the project is as follows:

1) Scrape articles from many diferent bengali news sources
    - Tools for this may be found under the bengali_article_scraping subdirectory. 
    Links were furnished by the SERP API and the articles will manually scraped form the webpages by a variety of methods.

2) Manually labels a collection of these articles 
    - A subset from the pool of articles were sampled and uploaded onto tagtog. The way in which they were sampled as well as various functions for loading tagtog files can be found in the bengali_data_management folder

3) Apply models to determine whether an article discussed flood, as well as models for determining the geotemporal location of floods and event detections.