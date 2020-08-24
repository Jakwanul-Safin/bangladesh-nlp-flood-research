"""
NewsAPI querying - only available for 1 month prior in free plan
"""

import requests
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
load_dotenv()

def make_params(query, date_start=datetime.now(), date_end=datetime.now() + timedelta(days=-31)):
    """
    make parameter dict to pass to newsAPI
    :param query:
    :param date_start:
    :param date_end:
    :return:
    """
    query_r = {
        'query': query.replace('AND','').replace('+','"'),
        'date_range': [date_start, date_end]
    }
    params = {
        "q": query,
        # "from": datetime.strptime(date_start, '%d/%m/%Y').isoformat(),
        # "to": datetime.strptime(date_end, '%d/%m/%Y').isoformat(),
        "from": date_start.isoformat(),
        "to": date_end.isoformat(),
        "language": 'en',
        "apiKey": os.getenv('NEWSAPI_KEY')
    }
    return query_r, params


query_terms, isBangla = ['flood', 'floods', 'flooding', 'flooded', 'cyclone', 'inundation', 'inundations', 'innundated'], False
queries = ['bangladesh AND {}'.format(term) for term in query_terms] + \
          ['bangladesh AND +{}'.format(term) for term in query_terms]


query_r, params = make_params(queries[0])
response = requests.get(url='http://newsapi.org/v2/everything', params=params)
json.dump(response.json(), open('newsAPI_trial.json','w'), indent=2)
