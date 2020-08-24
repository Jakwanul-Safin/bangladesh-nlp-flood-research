# Bangladesh NLP Flood Research
Code repository for Bangladesh NLP Flood Research Project

## Tagtog
Get data from tagtog, upload data to tagtog

### Data
Get data using `./get_shape_files.sh`. 1 folders will be downloaded: shammun_geography_dbf.
* shammun_geography_dbf - Contains shape file for district, division and upazilla

### Important Files
* extract_geography.py - Get list of districts, divisions and upazillas from shammun_geography_dbf
* tagtog_website.py - Download, upload data from tagtog. Common queries are in queries.txt