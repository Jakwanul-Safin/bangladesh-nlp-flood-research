# Bangladesh NLP Flood Research
Code repository for Bangladesh NLP Flood Research Project

## Classifier
Train and test classifier. Time series plotting. Data Comparison

### Data
Get data using `./get_classifier_data.sh`. 3 folders will be downloaded: data, other_data, timeseries_data.
<br/> A soft link to all_papers.py and paper_data (if downloaded) from article_scraping folder will be added.
<br/><span style="color:blue">Divisions (7): Barisal, Chittagong, Dhaka, Khulna, Rajshahi, Rangpur, Sylhet</span>
* data - Contains article data. Data loading methods can be found in functions.py and also in classifier.ipynnb
    * isflood.json - Contains is flood data
    * not_isflood.json - Contains not is flood data
* other_data - Comparison data
    * pmv_cm_ts - Passive Microwave C/M Ratio timeseries from 2017 - 2019 for Rajshahi and Sylhet Divisions
    * pmw_flood_ts - Passive Microwave Flood Area timeseries from 2017 - 2019 for Rajshahi and Sylhet Divisions
    * Sentinel1_ts - Sentinel 1 timeseries from 2017 - 2019 for Rajshahi and Sylhet Divisions
    * Damage data_Hassan.csv - Red Cross damage data for Bangladesh floods 
    * emdat_flood.csv - EMDAT damage data for Bangladesh floods 
    * Flood_Affected_Area_Barchart.csv - Government Flood area affected data for Bangladesh floods
* timeseries_data - All the different timeseries data
<br/><span style="color:red">Data can be inconsistent (not all years in between the range given will have data)</span>
    * [division-name].json - Division Monthly and yearly number of article published data (1985 - 2020)
    * yearPublished_day_[division-name].json - Division daily number of article published data (1985 - 2020)
    * district_articles_dist.json - District Monthly and yearly number of article published data (1985 - 2020)
    * international_newspaper.json - International Newspaper (nytimes) Monthly and yearly number of article published data (1985 - 2020)
    * national_newspaper.json - National Newspaper Monthly and yearly number of article published data (1985 - 2020)
    * site_distribution.json - Yearly number of article published data (1985 - 2020)
    * under_division.json - Mapping of districts located under divisions
    * under_district.json - Mapping of upazilas located under districts

### Important Files
* functions.py - Main file for classifying data
    * `load_data_tagtog` = loads tagtog data. Data folder/list of files can be given
    * `load_data` = loads data for classifier. Data folder/list of files/single file can be given. Supports data balancing
    * `make_data_ratio` = makes data ratio. Pass dataframe and test_size. Check implementation for additional parameters
* classifier.ipynb - Data loading, training different classifiers, testing, classifying new data
* timeseries.ipynb - Data loading, extracting datePublished, district and division from data
    * Timeseries for yearly and year-month distribution of articles published for different divisions
    * Distribution of articles based on district (De-trending method)
* compare_data.ipynb - Compare different time series
    * Timeseries for yearly and year-month distribution of articles published for different divisions
    * Passive Microwave, Sentinel-1, EMDAT, Government, Red Cross
    * Distribution of articles based on district (De-trending method)