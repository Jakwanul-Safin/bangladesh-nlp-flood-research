import os
from shutil import copyfile
import json
import re
from copy import deepcopy
import shutil
from unidecode import unidecode
import requests
from datetime import datetime
from datefinder import find_dates
import dateparser
from bs4 import BeautifulSoup
from uuid import uuid4
import re
from urllib.parse import urlparse
from collections import defaultdict
import matplotlib.pyplot as plt
from typing import Union, Optional
from selenium import webdriver

root_folder = '/Users/tejitpabari/Desktop/BangladeshFloodResearch/nlp_flood_research/article_scraping/paper_data'

def parse_paper_name(paper_name: Union[str, int]) -> str:
    """
    Forms Paper name using Paper Index Integer or Paper Name
    :param paper_name: Paper Index Integer; Name of Paper
    :return: Name of Paper
    """

    if type(paper_name)==int:
        save_paper_index_file = os.path.join(root_folder,'paper_index.json')
        file = json.load(open(save_paper_index_file))
        file2 = {int(k): v['paper_name'] for k, v in file.items()}
        file2[-1] = 'nytimes'
        return file2[paper_name]
    else:
        if paper_name=='nytimes': return 'nytimes'
        return paper_name

def parse_file_num(paper_name: str, merged_file_num: Union[str,int]='auto', file_type: str='sites') -> str:
    """
    Returns the next file number for the given paper
    :param paper_name: Name of Paper, parsed using parse_paper_name
    :param merged_file_num: File Label Number or
                            'auto' to auto take the number after last file number in folder or
                            'first' to take the first file number, i.e. 1
    :param file_type: Type of file to parse.
                      'sites' for sites and 'data' for data. Default = 'sites'
    :return:
    """
    paper_name = os.path.join(root_folder,parse_paper_name(paper_name))
    file_type_parse = '_sites.json' if file_type=='sites' else '_data.json'
    if type(merged_file_num) == str and merged_file_num == 'first': return '1'
    elif type(merged_file_num) == str and merged_file_num == 'auto':
        files = [f.split('_')[0] for f in os.listdir(paper_name) if file_type_parse in f]
        nums = []
        for f in files:
            r = re.findall(r'\d+', f)
            if r and len(r) > 0:
                nums.append(int(r[-1]))
            else:
                nums.append(0)
        merged_file_num = sorted(nums, reverse=True)[0] + 1
    return str(merged_file_num)


def get_all_paper_data(all_data_files = True) -> None:
    """
    Copies files labelled <paper_name>1_data.json from all newspapers to all_paper_data folder
    :return: None
    """
    save_folder = os.path.join(root_folder,'all_paper_data')
    folders = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder,f))]
    folders.remove('all_paper_data')
    if os.path.join(root_folder,'__pycache__') in folders:
        folders.remove(os.path.join(root_folder,'__pycache__'))
    if '__pycache__' in folders:
        folders.remove('__pycache__')

    for f in folders:
        if all_data_files:
            data_files = [ff for ff in os.listdir(os.path.join(root_folder,f)) if '_data' in ff]
        else:
            data_files = [f+'1_data.json']
        for file_name in data_files:
            data_file = os.path.join(root_folder, f,file_name)
            save_file = os.path.join(save_folder,file_name)
            if os.path.exists(data_file): copyfile(data_file, save_file)


def merge_paper_sites(paper_name: str, merged_file_num: Union[str, int]='first', delete_rest: bool=True, ignore_files =None) -> None:
    """
    Merges sites from different site files into 1 file.
    :param paper_name: parse_paper_name()
    :param merged_file_num: parse_file_num()
    :param delete_rest: delete rest of the files post merging the files
    :return: None
    """
    if not ignore_files: ignore_files = []
    merged_file_num = parse_file_num(paper_name, merged_file_num)
    paper_name = parse_paper_name(paper_name)
    folder = '{}/{}/'.format(root_folder, paper_name)
    sites_files = [f for f in os.listdir(folder) if '_sites' in f not in ignore_files]
    all_data, all_sites = [],set()
    for site_file in sites_files:
        data = json.load(open(folder+site_file))
        for d in data:
            check=True
            for i,d2 in enumerate(all_data):
                if d['query']==d2['query'] and \
                (d['date_range'][0]==d2['date_range'][0] and d['date_range'][1]==d2['date_range'][1]) and \
                d['paper']==d2['paper']:
                    all_data[i]['sites'] = [i for i in set(all_data[i]['sites']+d['sites']) if i not in all_sites]
                    all_sites = all_sites.union(all_data[i]['sites'])
                    check=False
                    break
            if check:
                d_sites = [i for i in d['sites'] if i not in all_sites]
                all_sites = all_sites.union(d['sites'])
                new_d = deepcopy(d)
                new_d['sites'] = d_sites
                all_data.append(new_d)
    total_site_count = sum([len(d['sites']) for d in all_data])
    print('Total Sites:',total_site_count)
    save_file = folder+paper_name+merged_file_num+'_sites.json'
    json.dump(all_data, open(save_file,'w'),indent=2)
    if delete_rest:
        if paper_name+merged_file_num+'_sites.json' in sites_files:
            sites_files.remove(paper_name+merged_file_num+'_sites.json')
        for s in sites_files: os.remove(folder+s)

def merge_data(paper_name: str, merged_file_num: Union[str, int]='first', delete_rest: bool=True) -> None:
    """
    Merges data from different data files into 1 file
    :param paper_name: parse_paper_name()
    :param merged_file_num: parse_file_num()
    :param delete_rest: delete rest of the files post merging the files
    :return: None
    """
    merged_file_num = parse_file_num(paper_name, merged_file_num, file_type='data')
    paper_name = parse_paper_name(paper_name)
    folder = '{}/{}/'.format(root_folder, paper_name)
    data_files = [f for f in os.listdir(folder) if '_data' in f]
    all_data, all_sites = [],set()
    for data_file in data_files:
        data = json.load(open(folder + data_file))
        if not all_data:
            all_data = data
            all_sites = set([d['meta']['link'] for d in data])
        else:
            for d in data:
                if d['meta']['link'] not in all_sites:
                    all_data.append(d)
                    all_sites.add(d['meta']['link'])
    print('Total Sites:', len(all_data))
    save_file = folder + paper_name + merged_file_num + '_data.json'
    json.dump(all_data, open(save_file, 'w'), indent=2)
    if delete_rest:
        if paper_name + merged_file_num + '_data.json' in data_files:
            data_files.remove(paper_name + merged_file_num + '_data.json')
        for s in data_files: os.remove(folder + s)

def merge_data_folder(paper_name: str, merged_file_num: Union[str, int]='first', delete_data_folder: bool=True) -> None:
    merged_file_num = parse_file_num(paper_name, merged_file_num, file_type='data')
    paper_name = parse_paper_name(paper_name)
    folder = '{}/{}/'.format(root_folder, paper_name)
    data_folder = folder + 'data/'
    if not os.path.isdir(data_folder): raise Exception('Cannot find Data Folder in Newspaper:',paper_name)
    data_files = [f for f in os.listdir(data_folder) if '.json' in f]
    all_data, all_sites = [], set()
    for data_file in data_files:
        data = json.load(open(data_folder + data_file))
        if not all_data:
            all_data = data
            all_sites = set([d['meta']['link'] for d in data])
        else:
            for d in data:
                if d['meta']['link'] not in all_sites:
                    all_data.append(d)
                    all_sites.add(d['meta']['link'])
    print('Total Sites:', len(all_data))
    save_file = folder + paper_name + merged_file_num + '_data.json'
    json.dump(all_data, open(save_file, 'w'), indent=2)
    if delete_data_folder: shutil.rmtree(data_folder)


def count_sites(paper_name: str, site_file_num='first') -> int:
    """
    Counts the number of sites for a given paper
    :param paper_name: name of paper/index of paper as per paper_inde.json
    :param site_file_num: which site file to choose to count number of sites
    :return: number of sites in newspaper
    """
    site_file_num = parse_file_num(paper_name, site_file_num)
    paper_name = parse_paper_name(paper_name)
    site_file = '{}/{}/{}{}_sites.json'.format(root_folder, paper_name, paper_name, site_file_num)
    all_data = json.load(open(site_file))
    total_site_count = sum([len(d['sites']) for d in all_data])
    return total_site_count

def count_sites_all_paper(bangla: bool = False, english: bool = False, site_file_num= 'first') -> int:
    """
    Count number of sites in app papers
    :param bangla: count bangla papers
    :param english: count english papers
    :param site_file_num: which site file to choose to count number of sites
    :return: number of sites
    """
    save_paper_index_file = os.path.join(root_folder,'paper_index.json')
    file = json.load(open(save_paper_index_file))
    papers = [f['paper_name'] for f in file.values()]
    s = []
    for paper in papers:
        if not bangla:
            if '-bangla' not in paper:
                s.append(count_sites(paper, site_file_num))
        elif not english:
            if '-bangla' in paper:
                s.append(count_sites(paper, site_file_num))
        else: s.append(count_sites(paper, site_file_num))
    return sum(s)


def get_paper_site(paper_name: str) -> Union[str, None]:
    """
    Get the root url for a given paper (assuming a _sites file exists for the paper
    :param paper_name: name of paper
    :return: root url for paper
    """
    paper_name = parse_paper_name(paper_name)
    site_file = os.path.join(root_folder, paper_name, paper_name + '1_sites.json')
    if os.path.exists(site_file):
        site_data = json.load(open(site_file))
        for s in site_data:
            if s['sites'] and len(s['sites'])>0:
                return urlparse(s['sites'][0]).hostname
    return None


def get_date_range(paper_name: str):
    """
    Get the date range (years) for which sites exist for the given paper name
    :param paper_name: name of paper
    :return: min year and max year for date range
    """
    paper_name = parse_paper_name(paper_name)
    site_file = os.path.join(root_folder, paper_name, paper_name + '1_sites.json')
    if os.path.exists(site_file):
        site_data = json.load(open(site_file))
        dmin, dmax = float('inf'), 0
        for s in site_data:
            year = int(s['date_range'][0].split('/')[-1])
            dmin = min(year, dmin)
            dmax = max(year, dmax)
        return dmin, dmax
    return None, None

def get_last_date(paper_name: str) -> Union[str, None]:
    """
    Get the last date for the given newspaper, for which a site has been scraped
    :param paper_name: name of paper
    :return: date string
    """
    paper_name = parse_paper_name(paper_name)
    site_file = os.path.join(paper_name, paper_name + '1_data.json')
    if os.path.exists(site_file):
        site_data = json.load(open(site_file))
        dmin = datetime(1000, 1, 1)
        for s in site_data:
            last_date = dateparser.parse(s['date_range'][1])
            dmin = max(dmin, last_date)
        return dmin
    return None

def iterate_all_papers(bangla=False, english=False):
    """
    iterator through all papers whose folder exist
    :param bangla: consider bangla papers
    :param english: consider english newspapers
    :return:
    """
    if not bangla and not english: raise Exception('English or Bangla or both must be true')
    remove_folders = ['__pycache__', 'all_paper_data']
    papers = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder,f))]
    bangla_papers = [f for f in papers if '-bangla' in f]
    if not bangla: remove_folders+=bangla_papers
    for remove_paper in remove_folders:
        if remove_paper in papers: papers.remove(remove_paper)
    for paper in papers:
        yield paper

def iterate_all_paper_data(data=False):
    folder_path = os.path.join(root_folder, 'all_paper_data')
    for f in os.listdir(folder_path):
        fp = os.path.join(folder_path, f)
        if '.json' in f:
            if data: yield json.load(open(fp))
            else: yield fp


def generate_paper_index():
    """
    Make paper index file
    :return:
    """
    save_paper_index_file = os.path.join(root_folder,'paper_index.json')
    remove_folders = ['__pycache__', 'all_paper_data']
    papers = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder,f))]
    bangla_papers = [f for f in papers if '-bangla' in f]
    remove_folders += bangla_papers
    for remove_paper in remove_folders:
        if remove_paper in papers: papers.remove(remove_paper)
    # papers = sorted(papers) + sorted(bangla_papers)
    d_list = []
    for i, name in enumerate(papers):
        dmin, dmax = get_date_range(name)
        d_list.append({
            'paper_name': name,
            'site': get_paper_site(name),
            'no_sites': count_sites(name),
            'date_range': '{}-{}'.format(dmin, dmax)
        })
    d_list.sort(key= lambda x:x['no_sites'], reverse=True)

    d_list2 = []
    for i, name in enumerate(bangla_papers):
        dmin, dmax = get_date_range(name)
        d_list2.append({
            'paper_name': name,
            'site': get_paper_site(name),
            'no_sites': count_sites(name),
            'date_range': '{}-{}'.format(dmin, dmax)
        })
    d_list2.sort(key=lambda x: x['no_sites'], reverse=True)
    d = {i+1: v for i,v in enumerate(d_list + d_list2)}
    json.dump(d, open(save_paper_index_file, 'w'), indent=2)

def parse_date(date_obj):
    """
    parse date from date object or string
    :param date_obj:
    :return:
    """
    if not date_obj: return None
    elif type(date_obj)==datetime:
        return date_obj
    else:
        dates = [f for f in find_dates(date_obj)]
        if dates: return dates[0]
    return None
    # sp = date_obj.split('T')
    # year, month, day = sp[0].split('-')
    # sp =
    # return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    """
    get content from soup object
    :param soup_obj:
    :return:
    """
    if not soup_obj: return None
    return soup_obj.get('content')

def get_meta(soup, site):
    """
    Get metadata from soup and site url
    :param soup: Beautiful soup object
    :param site: Site url
    :return: dict of metadata. Mainly: datePublished
    """
    description = get_content(soup.find('meta', attrs={'name': 'description'}))

    abstract = get_content(soup.find('meta', attrs={'name': 'abstract'}))
    keywords = get_content(soup.find('meta', attrs={'name': 'keywords'}))
    if keywords: keywords = [s.strip() for s in keywords.split(',')]
    news_keywords = get_content(soup.find('meta', attrs={'name': 'news_keywords'}))

    datePublished = get_content(soup.find('meta', attrs={'name': 'article:published_time'}))
    if not datePublished: datePublished = get_content(soup.find('meta', property='article:published_time'))
    if not datePublished: datePublished = get_content(soup.find('meta', property='publish-date'))
    if not datePublished: datePublished = get_content(soup.find('meta', attrs={'name': 'publish-date'}))
    if not datePublished:
        matches = re.search(r'\d{4}/\d{2}/\d{2}',site)
        if matches: datePublished = matches[0].replace('/','-')
    if not datePublished:
        matches = re.search(r'\d{4}-\d{2}-\d{2}',site)
        if matches: datePublished = matches[0]
    if not datePublished:
        matches = [f for f in find_dates(site)]
        if matches: datePublished = matches[0]
    if datePublished: datePublished = parse_date(datePublished)
    dateModified = get_content(soup.find('meta', property='article:modified_time'))
    if dateModified: dateModified = parse_date(dateModified)

    if abstract: abstract = unidecode(abstract)
    if description: description = unidecode(description)
    if datePublished: datePublished = str(datePublished)
    if dateModified: dateModified = str(dateModified)

    return {
        'abstract': abstract,
        'news_keywords':news_keywords,
        'description': description,
        'keywords': keywords,
        'datePublished': datePublished,
        'dateModified': dateModified,
    }

def get_soup(site, selenium=False):
    """get soup object"""
    if selenium:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path='/Applications/chromedriver', options=options)
        driver.get(site)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    else:
        page = requests.get(site)
        soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def scrape_inner(paper_name: str, paper_func: object, sites_i=None, debug: bool=True, sites: list=None,
                 main_data_sites: set=None, selenium: bool=False):
    """
    Scrape using scrape function and return scraped data
    :param paper_name: name of paper
    :param paper_func: paper function to scrape using
    :param sites_i: single site url for article (in case of single site)
    :param debug: debug param
    :param sites: list of sites
    :param main_data_sites: sites already done
    :param selenium: toggle selenium on or off
    :return: list of site data for given sites.
    """
    data_folder = os.path.join(root_folder, paper_name,'data')
    query_info = None
    query = ''
    if not sites:
        sites = sites_i['sites']
        if main_data_sites: sites = list(set(sites)-main_data_sites)
        query_info = {"query": sites_i['query'], "paper": sites_i['paper'], "date_range": sites_i['date_range']}
        query = '-'.join(sites_i['query'].replace('"', 'QQ').split(' '))

    site_data = []
    for i, site in enumerate(sites):
        try:
            soup = get_soup(site, selenium=selenium)
            meta = get_meta(soup, site)
            meta['link'], meta['query_info'] = site, query_info
            article = paper_func(soup, meta)
            if 'datePublished' in article and article['datePublished']:
                meta['datePublished'] = article['datePublished']
                # if not meta['datePublished']: meta['datePublished'] = article['datePublished']
                del article['datePublished']
            data = {
                'meta': meta,
                'article': article,
                'id': str(uuid4())
            }
            site_data.append(data)
            if i%10==0: print('.', end='')
        except Exception as e:
            print(e)
            print(site)
            continue
    if debug:
        debug_date = [s.replace('/','-') for s in sites_i['date_range']]
        print('Query:{}. Date Range: {}-{}. Sites scraped: {}'.format(query[:50], debug_date[0], debug_date[1], len(site_data)))
        save_file = open(os.path.join(data_folder, 'query_{}.data_{}-{}.json'.format(query, debug_date[0], debug_date[1])), 'w')
        json.dump(site_data, save_file, indent=2)
        save_file.close()
    print()
    return site_data

def scrape_main(paper_name: str, data_file_num='first', site=None, debug=True, site_file_num='first', selenium=False):
    """
    Wrapper around scrape inner. Handles storing to file, getting the respective function based on newspaper etc
    :param paper_name:
    :param data_file_num:
    :param site:
    :param debug:
    :param site_file_num:
    :param selenium:
    :return:
    """
    from article_scrapes.dhakaTribune_scrape import dhakaTribuneScrape
    from article_scrapes.theDailyStar_scrape import theDailyStarScrape
    from article_scrapes.dailySun_scrape import dailySunScrape
    from article_scrapes.bdnews_scrape import bdnewsScrape
    from article_scrapes.prothomalo_scrape import prothomaloScrape
    from article_scrapes.theIndependent_scrape import theIndependentScrape
    from article_scrapes.theNewNation_scrape import theNewNationScrape
    from article_scrapes.dailyObserver_scrape import dailyObserverScrape
    from article_scrapes.newAge_scrape import newAgeScrape

    func_dict = {
        'dhakaTribune': dhakaTribuneScrape,
        'theDailyStar': theDailyStarScrape,
        'dailySun': dailySunScrape,
        'bdnews': bdnewsScrape,
        'prothomalo': prothomaloScrape,
        'theIndependent': theIndependentScrape,
        'theNewNation': theNewNationScrape,
        'dailyObserver': dailyObserverScrape,
        'newAge': newAgeScrape
    }

    if paper_name not in func_dict: raise Exception('Please add a function for paper',paper_name)
    paper_name = parse_paper_name(paper_name)
    data_file_num = parse_file_num(paper_name, data_file_num, file_type='data')
    site_file_num = parse_file_num(paper_name, site_file_num)

    data_folder_path = os.path.join(root_folder, paper_name,'data')
    if os.path.isdir(data_folder_path): shutil.rmtree(data_folder_path)
    os.mkdir(data_folder_path)

    sites_file_path = os.path.join(root_folder, paper_name, paper_name + site_file_num + '_sites.json')
    data_file_path = os.path.join(root_folder, paper_name, paper_name + data_file_num + '_data.json')

    main_data_file_path = os.path.join(root_folder, paper_name, paper_name + '1_data.json')
    main_data_sites = set()
    if os.path.exists(main_data_file_path):
        main_data_file = json.load(open(main_data_file_path))
        main_data_sites = set([i['meta']['link'] for i in main_data_file])

    site_file = open(sites_file_path)
    sites_i = json.load(site_file)
    scrapped = []
    for s in sites_i:
        sites_data = scrape_inner(paper_name, func_dict[paper_name], s, debug, site, main_data_sites, selenium=selenium)
        scrapped.extend(sites_data)
        if main_data_sites:  main_data_sites = main_data_sites.union(set([i['meta']['link'] for i in sites_data]))
        else: main_data_sites = set([i['meta']['link'] for i in sites_data])
    scrapped = []
    for file in [f for f in os.listdir(data_folder_path) if '.json' in f]:
        scrapped.extend(json.load(open(os.path.join(data_folder_path, file))))
    print('Total Sites scrapped: {}'.format(len(scrapped)))
    save_file = open(data_file_path, 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    site_file.close()

all_terms = ['meta', 'article', 'id']
meta_terms = ['link', 'description', 'keywords', 'datePublished', 'dateModified', 'query_info']
query_info_terms = ['query', 'date_range']
article_terms = ['headline', 'authors', 'text']

def make_id_filename(filename):
    """
    get id from filename
    :param filename: file name
    :return:
    """
    doc_id=None
    if '.ann' in filename or '.txt' in filename or '.json' in filename or '_data_' in filename:
        filename2 = filename.replace('.ann', '').replace('.txt', '').replace('.json', '')
        if ('_data_') in filename2:
            splt = filename2.split('_data_')
            if len(splt) > 1:
                doc_id = splt[1].replace('_', '-')
            else:
                raise Exception('Unable to extract id')
        else:
            return filename2
    else: doc_id = filename
    return doc_id

def make_newspaper_filename(filename: str):
    """
    get newspaper from filename
    :param filename:
    :return:
    """
    if '_data_' in filename:
        splt = filename.split('_data_')
        return splt[0]
    elif '.ann' in filename or '.txt' in filename or '.json' in filename: return None
    else: return filename

def get_id_data(query_id=None, connect_filename=None, query_term='all', debug=True):
    """
    given an id or connect_filename, get data related to it
    :param paper_name:
    :param query_id:
    :param connect_filename:
    :param query_term: 'all' to get all data, or enter a term to query (eg. datePublished)
    :param debug:
    :return:
    """
    data_id = None
    for data in iterate_all_paper_data(data=True):
    # data = json.load(open(os.path.join(root_folder, 'all_paper_data',paper_name+'1_data.json')))
        if query_id:
            for d in data:
                if d['id']==query_id:
                    data_id=d
                    break
        elif connect_filename:
            for d in data:
                if 'connect_filename' in d and d['connect_filename']==connect_filename:
                    data_id=d
                    break
        else: raise Exception('Please enter a query_id or a connect_filename')
    if not data_id: raise Exception('ID: {} not found'.format(query_id))

    if query_term=='all': return data_id
    else:
        if query_term in all_terms: return data_id[query_term]
        elif query_term in meta_terms:
            meta = data_id['meta']
            return meta[query_term]
        elif query_term in query_info_terms:
            query_info = data_id['meta']['query_info']
            return query_info[query_term]
        elif query_term in article_terms:
            article = data['article']
            return article[query_term]
        else:
            raise Exception('Cannot find query term: {} in data'.format(query_term))


def site_distribution():
    """
    Get graph of site distribution.
    Data saved in site_distribution.json
    Figure saved in site_distribution.png
    :return:
    """
    sites = defaultdict(set)
    for paper in iterate_all_papers(english=True):
        for query in json.load(open(os.path.join(root_folder, paper, paper+'1_sites.json'))):
            date = query['date_range'][0]
            year = dateparser.parse(date).year
            sites[year] = sites[year].union(set(query['sites']))
    site_counts = defaultdict(int)
    for k,v in sites.items(): site_counts[k]+=len(v)
    for entry in json.load(open(os.path.join(root_folder, 'all_paper_data/nytimes1_data.json'))):
        try:
            year = dateparser.parse(entry['meta']['datePublished']).year
            site_counts[year]+=1
        except Exception as e:
            print(e, entry['id'])
            continue
    json.dump(site_counts, open('site_distribution.json','w'), indent=2)
    print('Total Sites Scraped:',sum(site_counts.values()))
    plt.figure(figsize=(15,10))
    plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
    plt.rcParams['ytick.left'] = plt.rcParams['ytick.labelleft'] = False
    plt.rcParams['font.size']=16
    plt.bar(list(site_counts.keys()), list(site_counts.values()))
    plt.xlabel('Year of Publishing')
    plt.ylabel('# of Articles', labelpad=-980)
    plt.title('# of Articles vs Year of Publishing')
    plt.savefig('site_distribution.png')
    # plt.tick_params(axis='y', which='right', labelleft='off', labelright='on')
    plt.show()


def scraped_data_distribution():
    """
    Get graph of scraped data distribution
    Data Saved in scraped_data_distribution.json
    Figure saved in scraped_data_distribution.png
    :return:
    """
    data_year = defaultdict(int)
    data_year_month = defaultdict(int)
    for filename in [os.path.join(root_folder, 'all_paper_data',f)
                     for f in os.listdir(os.path.join(root_folder, 'all_paper_data')) if '.json' in f]:
        js = json.load(open(filename))
        for entry in js:
            date = entry['meta']['datePublished']
            if date:
                try:
                    datePublished = dateparser.parse(date, settings={'RELATIVE_BASE': datetime(1400, 1, 1)})
                    year, month = datePublished.year, datePublished.month
                    if year < 1980: raise Exception('No Date Present', date)
                    if year == 1400: raise Exception('No Year Present')
                    if year > 2020: raise Exception('No Date Present', date)
                    data_year[year] += 1
                    year_month = '{}-{:02d}'.format(year,month)
                    data_year_month[year_month] += 1
                except Exception as e:
                    print(e)
                    print(date, entry['id'], filename)
                    continue
    total_data = {'data_year': data_year, 'data_year_month': data_year_month}
    json.dump(total_data, open('scraped_data_distribution.json', 'w'), indent=2)
    year_l = sorted([(k,v) for k,v in data_year.items()])
    # print('Total Sites Scraped:',sum(data_year.values()))

    plt.figure(figsize=(15, 10))
    plt.rcParams['font.size'] = 16
    plt.bar([i[0] for i in year_l], [i[1] for i in year_l])
    plt.xlabel('Year of Publishing')
    plt.tick_params(axis='y', which='both', labelleft=False, labelright=True)
    plt.ylabel('# of Articles', labelpad=-980)
    plt.savefig('scraped_data_distribution.png')
    # plt.title('# of Articles scraped vs Year of Publishing')
    plt.show()

    # print(data_year, data_year_month)


def get_all_sites():
    """
    get all sites already done.
    Data saved in all_sites.json
    :return:
    """
    save_folder = os.path.join(root_folder, 'all_paper_data')
    file = [f for f in os.listdir(save_folder) if '.json' in f]
    all_sites = set()

    for f in file:
        fo = json.load(open(os.path.join(save_folder, f)))
        for entry in fo:
            url = entry['meta'].get('link',None)
            if url:
                all_sites.add(url)
                # edge cases
                if 'm.thedailynewnation.com' in url: all_sites.add(url.replace('m.thedailynewnation.com', 'thedailynewnation.com'))
    json.dump(list(all_sites), open('all_sites.json','w'), indent=2)


"""
Completed:
    bdnews, dailySun, dhakaTribune, nytimes, prothomalo, dailyStar, 
    dailyObserver, theNewNation, theIndependent
"""





if __name__=='__main__':
    # scrape_main('theIndependent', data_file_num='2', site_file_num='2', selenium=True)
    # print(get_last_date('bdnews'))
    scraped_data_distribution()
    # get_all_paper_data()
    # get_all_sites()
    # paper_name = 'theNewNation'
    # merge_paper_sites(paper_name, 2, True, ignore_files=['{}1_sites.json'.format(paper_name)])
    # generate_paper_index()
    # print(count_sites_all_paper(english=True))
    # for paper in iterate_all_papers(english=True):
    #     merge_paper_sites(paper)
    # merge_paper_sites('theDailyStar')
    # scrape_main('dailySun', data_file_num='auto')
    # newspapers = ['bdnews', 'dailySun', 'prothomalo', 'dailyObserver', 'newAge',
    #               'dhakaTribune', 'theDailyStar', 'theIndependent', 'theNewNation']
    # for paper in newspapers:
    #     merge_paper_sites(paper)
    # site_distribution()
    # get_all_sites()
    pass

# print('Bangla Sites:',count_sites_all_paper(bangla=True)
#       , 'English Sites:', count_sites_all_paper(english=True))
# get_all_paper_data()
# merge_data('dhakaTribune',0,True)
# generate_paper_index()

# merge_paper_sites('dailySun')

# folders = [f for f in os.listdir('./') if os.path.isdir(f)]
# folders.remove('__pycache__')
#
# for f in folders:  os.system('cd '+f+'; touch __init__.py; cd ..')
