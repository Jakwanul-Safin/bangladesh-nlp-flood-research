import requests
import json

url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/NewsSearchAPI"


querystring = {"fromPublishedDate":"01/01/2014",
               "toPublishedDate":"01/31/2014",
               "autoCorrect":"false",
               "pageNumber":"1",
               "pageSize":"10",
               "q":"bangladesh floods",
               "safeSearch":"false"}

headers = {
    'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com",
    'x-rapidapi-key': "06581d785fmsh3e1138175250449p12db1bjsnbf6adb345a75"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

json.dump(json.loads(response.text), open('trial.json','w'), indent=2)