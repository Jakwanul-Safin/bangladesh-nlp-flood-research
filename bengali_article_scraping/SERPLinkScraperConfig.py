import os

import pickle, json, yaml
from datetime import timedelta, date, datetime

PAPER_SITES_FILE = "paper_to_site.json"
with open("paper_to_site.json", 'r') as f:
    paper_site = json.load(f)

class SERPLinkScraperConfig:
    def __init__(self, config_file = None):
        self.config = {
            "searchnws": False, 
            "gl": "bd", 
            "hl": "bn", 
            "filter": "0", 
            "num": 100,
            "output_dir": "",
            "output_file": "serp_{papers}_{query}.json",
            "quote_sub": "[QUOTE]",
            "overwrite": False,
            "skip_existing": True,
            "seen_sites_file": None,
            "completed_searches_file": None
        }
        
        if config_file is not None:
            self.load_config(config_file)
    
    def range_dates(self, date_start:date, date_end:date, increment:timedelta):
        """
        Helper function to get time intervals
        :param date_start: Starting date
        :param date_end: ending date
        :param increment: increments dates by value
        :return: list of dates
        """
        while date_start + increment < date_end:
            yield date_start, date_start + increment
            date_start += increment
        yield date_start, date_end

    def generate_dates_from_date_ranges(self, date_ranges):
        dates = []
        for start, end, inc in date_ranges:
            start = datetime.strptime(start, "%m/%d/%Y").date()
            end = datetime.strptime(end, "%m/%d/%Y").date()
            inc = timedelta(days=inc)
            dates.extend((s.strftime("%m/%d/%Y"), t.strftime("%m/%d/%Y")) for s, t in self.range_dates(start, end, inc))
        return dates
    
    def query_paper_date_from_spec(self, specs):
        if 'query' in specs:
            queries = [specs['query']]
        elif 'queries' in specs:
            queries = specs['queries']
        else:
            raise KeyError("Expecting 'queries' in config file")
        
        if 'paper' in specs:
            papers = [specs['paper']]
        elif 'papers' in specs:
            papers = specs['papers']
        else:
            raise KeyError("Expecting 'paper' in config file")
            
        unknown_papers = [paper for paper in papers if paper not in paper_site]
        if len(unknown_papers) > 0:
            raise KeyError("Unknown papers: {}\nPlease add to paper list".format(", ".join(unknown_papers)))
        
        if 'date_ranges' not in specs:
            raise KeyError("Expecting 'date_ranges' in config file")
        
        dates = self.generate_dates_from_date_ranges(specs['date_ranges'])
        
        for q in queries:
            for p in papers:
                for d in dates:
                    yield q, p, d  
    
    def params(self, query, paper, date_interval):
        site = paper_site[paper]
        start_date, end_date = date_interval
        params = {
            "engine": "google",
            "q": "{} site:{}".format(query, site),
            "google_domain": "google.com",
            "gl": self.config['gl'],
            "hl": self.config['hl'],
            'filter':self.config['filter'],
            "num": self.config['num'],
            "api_key": self.config['SERPAPI_KEY'],
            "tbs": "cdr:1,cd_min:{},cd_max:{}".format(start_date, end_date)
        }

        if self.config['searchnws']:
            params["tbm"] = "nws"

        return params 
    
    def update_config(self, config_file):
        with open(config_file, "r", encoding='utf-8') as f:
            self.config.update(yaml.load(f, Loader=yaml.FullLoader))
    
    def check_config(self):
        missing = [param for param in ('SERPAPI_KEY',) if param not in self.config]
        if len(missing) > 0:
            raise KeyError("Config missing: {}".format(", ".join(missing)))

    def load_config(self, config_file):
        self.update_config(config_file)
        self.check_config()
        
    def searches(self, spec = None):
        if spec is None:
            spec = self.config
            
        if "searches" in spec:
            for spec in self.config['searches'].values():
                for search in self.searches(spec):
                    yield search
        else:
            for query, paper, date in self.query_paper_date_from_spec(spec):
                yield query, paper, date, self.params(query, paper, date)
                
    def outfile(self):
        filename = self.config["output_file"]
        outdir = self.config["output_dir"] if 'output_dir' in self.config else ""
        return os.path.join(outdir, filename)
    
    def completed_searches(self):
        if self.config['completed_searches_file'] is not None and os.path.exists(self.config['completed_searches_file']):
            with open(self.config['completed_searches_file'], 'rb') as f:
                return pickle.load(f)
        return set()


    def store_completed_searches(self, completed_searches):
        if self.config['completed_searches_file'] is not None:
            with open(self.config['completed_searches_file'], 'wb') as f:
                return pickle.dump(completed_searches, f)

    def __repr__(self):
        return self.config.__repr__()

    def num(self):
        return self.config['num']
    
    def searchnews(self):
        return self.config['searchnws']