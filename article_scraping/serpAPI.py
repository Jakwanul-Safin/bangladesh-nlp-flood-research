"""
Get google news results from serpAPI
Need serpAPI key for this. Send an email to tvp2107@columbia.edu for the key
"""

import json
import os
import re
import sys
from serpapi.google_search_results import GoogleSearchResults
from dotenv import load_dotenv
load_dotenv()

root_folder = 'paper_data'

def make_params(query: str = "bangladesh floods", site: str = "www.thedailystar.net", date_start: str = '1/1/2020',
                date_end: str = '1/1/2021', num_results: int = 100, paper: str = 'theDailyStar') -> (dict,dict):
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
        'date_range': [date_start, date_end] if date_start!=date_end else date_start
    }
    params = {
        "engine": "google",
        "q": "{} site:{}".format(query, site),
        "google_domain": "google.com",
        "gl": "bd",
        "hl": "en",
        "tbm": "nws",
        'filter':'0',
        "num": num_results,
        "tbs": "cdr:1,cd_min:{},cd_max:{}".format(date_start, date_end),
        "api_key": os.getenv('SERPAPI_KEY')
    }
    return query_r, params

def make_dates(year_start:int=2014, year_end:int=2021, month_increment:int=0) -> list:
    """
    Make a list of dates to pass to serpAPI
    :param year_start: starting year
    :param year_end: ending year
    :param month_increment: increment months by. If 0, first and last months are chosen for that year
    :return: list of dates to pass to serpAPI
    """
    y = year_start
    dates = []
    while y!=year_end:
        if month_increment:
            # add dates incremented by month_increment
            m = 1
            while m<=12:
                end_month = m+month_increment if m+month_increment<=12 else 12
                end_date = 1 if m+month_increment<=12 else 31
                date = ['{}/1/{}'.format(m, y), '{}/{}/{}'.format(end_month, end_date, y)]
                if m == 12: date = ['12/1/{}'.format(y), '12/31/{}'.format(y)]
                m+=month_increment
                dates.append(date)
        else:
            # If month_increment == 0
            date = ['1/1/{}'.format(y), '12/31/{}'.format(y)]
            dates.append(date)
        y+=1
    return dates

def query_serp(query:str, site:str, dates:list, num_results:int, paper_name:str, check_sites_file=None) -> list:
    """
    Make dict for serp query using make_params()
    query serpAPI
    :param query: query string for google news
    :param site: site root url (eg. www.google.com)
    :param dates: list of dates
    :param num_results: number of results
    :param paper_name: name of paper
    :return: list of query dicts containing query information and sites list for the query
    """
    all_sites = []
    check_sites = set()
    if check_sites_file: check_sites = set(json.load(open(check_sites_file)))
    total_sites_count = 0

    for d in dates:
        try:
            # Get query dict and params dict
            query_r, params = make_params(query=query, site=site, date_start=d[0], date_end=d[1],
                                          num_results=num_results, paper=paper_name)
            # serpAPI query
            client = GoogleSearchResults(params)
            results = client.get_dict()
            news_results = results['news_results']

            count = 0
            sites_date = []
            # Loop through till end of search results or error encountered
            while (news_results and len(news_results)>0) or ('error' not in results):
                sites = [news['link'] for news in news_results if news['link'] not in check_sites]
                if not sites: break
                sites_date.extend(sites)
                count+=len(sites)

                params['start'] = count
                client = GoogleSearchResults(params)
                results = client.get_dict()
                news_results = results['news_results']

            print('Date Range: {}-{}\tTotal Sites: {}'.format(d[0],d[1],len(sites_date)))

            # add list of sites to query dict
            query_r['sites'] = sites_date
            all_sites.append(query_r)
            total_sites_count += len(sites_date)
        except Exception as e:
            print(e)
            print(d)
            continue
    print('Total Sites: {}'.format(total_sites_count))
    return all_sites

def query_serp_count(query, site, dates, num_results, paper_name):
    siteCounts = []
    totalSites = 0
    for i,d in enumerate(dates):
        try:
            # Get query dict and params dict
            query_r, params = make_params(query=query, site=site, date_start=d[0], date_end=d[1],
                                          num_results=num_results, paper=paper_name)
            # serpAPI query
            client = GoogleSearchResults(params)
            results = client.get_dict()
            siteC = results['search_information'].get('total_results',0)
            if siteC: siteC = int(siteC)
            else: siteC = 0

            query_r['site_count'] = siteC
            siteCounts.append(query_r)
            totalSites += siteC
        except Exception as e:
            print(e)
            print(d)
            continue
        if i%10==0: print('{} '.format(i),end='')
    print('\nTotal Sites: {}'.format(totalSites))
    return siteCounts

def generate_site_file_num(paper_name:str, file_num:str='auto') -> str:
    """
    Returns the next file number for sites file (if auto)
    :param paper_name: name of paper
    :param file_num: optional file number
    :return:
    """
    if type(file_num)==str and file_num=='auto':
        files = [f.split('_')[0] for f in os.listdir(os.path.join(root_folder, paper_name)) if '_sites.json' in f]
        nums = [0]
        for f in files:
            r = re.findall(r'\d+', f)
            if r and len(r)>0: nums.append(int(r[-1]))
            else: nums.append(0)
        file_num = sorted(nums, reverse=True)[0]+1
    return str(file_num)

def SERP(year_start, year_end, query, site, paper_name, num_results=100, file_num='auto', check_sites_file=None, month_increment=2):
    """
    Wrapper around query_serp. Takes care of making dates list, saving data
    :param year_start:
    :param year_end:
    :param query:
    :param site:
    :param paper_name:
    :param num_results:
    :param file_num:
    :return:
    """
    dates = make_dates(year_start=year_start, year_end=year_end, month_increment=month_increment)
    file_num = generate_site_file_num(paper_name, file_num)
    print('Paper: {}\tQuery: {}'.format(paper_name, query))
    all_sites = query_serp(query=query, site=site, num_results=num_results, paper_name=paper_name, dates=dates, check_sites_file=check_sites_file)
    add_to_file = 'w'
    save_file_path = os.path.join(root_folder, paper_name, '{}{}_sites.json'.format(paper_name, file_num))
    if add_to_file == 'a':
        if not os.path.exists(save_file_path): add_to_file = 'w'
    save_file = open(save_file_path, add_to_file)
    json.dump(all_sites, save_file, indent=2)
    save_file.close()

def isLeap(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def SERP_Count(year_start, year_end, query, site, paper_name, num_results=100, save_file='siteCounts.json', skipDay=5):
    dates = []
    for year in range(year_start, year_end+1):
        for months in range(1, 13):
            day_range = 31 if months in [1, 3, 5, 7, 8, 10, 12] else 30
            if months == 2:
                if isLeap(year): day_range = 29
                else: day_range = 28
            if year>=2020 and months>=10: break
            for day in range(1, day_range +1, skipDay):
                endDate = day+skipDay if day+skipDay<=day_range else day_range
                date = ['{}/{}/{}'.format(months, day, year), '{}/{}/{}'.format(months, endDate, year)]
                dates.append(date)
    data = {}
    prev_siteCounts = []
    if os.path.exists(save_file):
        data = json.load(open(save_file))
        if paper_name in data: prev_siteCounts = data[paper_name]
    prevDates = [i['date_range'] for i in prev_siteCounts]
    for d in prevDates:
        if [d,d] in dates: dates.remove([d,d])
    siteCounts = query_serp_count(query=query, site=site, num_results=num_results, paper_name=paper_name, dates=dates)
    prev_siteCounts += siteCounts
    prev_siteCounts.sort(key=lambda x:tuple(map(int, x['date_range'][0].split('/'))))
    data[paper_name] = prev_siteCounts
    json.dump(data, open(save_file,'w'), indent=2)



if __name__=='__main__':
#     query_terms, isBangla = ['flood', 'floods', 'flooding', 'flooded', 'cyclone', 'inundation', 'innundated'], False
#     divisions = ['barisal', 'chittagong', 'dhaka', 'khulna', 'rajshahi', 'rangpur', 'sylhet', 'mymensingh']
#     locations = divisions + ['bangladesh']
#     # Form different types of queries
#     query = '({}) ({})'.format(' OR '.join(locations), ' OR '.join(query_terms))
#     num_results = 100
#     # year_start = 2007
#     # year_end = 2020
#     year_start_list = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
#     year_end_list = [2015, 2016, 2017, 2018, 2019, 2020, 2021]
#     month_increments = [2,2,2,2,2,2,2]
#
#     # query, isBangla = "বাংলাদেশ বন্যা", True
#     site = "www.theindependentbd.com"
#     paper_name = 'theNewNation'
#     for i in range(len(year_end_list)):
#         year_start, year_end, month_increment = year_start_list[i], year_end_list[i], month_increments[i]
#         SERP(year_start, year_end, query, site, paper_name, num_results, check_sites_file='all_sites.json', month_increment=month_increment)
    query = 'and'
    # paper_name, site, skipDay = 'theNewNation', "http://thedailynewnation.com/", 5
    # paper_name, site, skipDay = 'theDailyStar', 'https://www.thedailystar.net', 5
    # paper_name, site, skipDay = 'bdnews', 'https://bdnews24.com', 5
    # paper_name, site, skipDay = 'dailyObserver', 'https://www.observerbd.com', 15
    # paper_name, site, skipDay = 'dailySun', 'https://www.daily-sun.com', 5
    # paper_name, site, skipDay = 'dhakaTribune', 'https://www.dhakatribune.com/', 7
    # paper_name, site, skipDay = 'newAge', 'https://www.newagebd.net', 15
    # paper_name, site, skipDay = 'prothomalo', 'https://en.prothomalo.com', 15
    paper_name, site, skipDay = 'theIndependent', 'http://www.theindependentbd.com', 7
    num_results = 100
    year_start = 2014
    year_end = 2017
    SERP_Count(year_start, year_end, query, site, paper_name, num_results, skipDay=skipDay)