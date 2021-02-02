import os
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})
import numpy as np
from all_papers import make_id_filename, get_id_data, make_newspaper_filename

"""
type = m_6
newspaper = m_30
is_flood = m_28
flood_related = m_57
is_bangladesh = m_55
flood-climatechange = m_33
"""

def extract_dates(entity, debug=False):
    fields = entity.get('fields',None)
    if fields:
        f_51 = fields.get('f_51',None)
        f_50 = fields.get('f_50',None)
        if f_51:
            date = f_51.get('value',None)
            if date: return date
            else:
                if debug: print('No Date in f_51 fields')
        else:
            if debug: print('No f_51 in fields')
    else:
        if debug: print('NO DATE')
        return None

def get_data_json(file, folder, debug=False):
    filepath = os.path.join(folder, file)
    js = json.load(open(filepath))

    filename = js.get('filename',None)
    doc_id = None
    if filename:
        filename2 = filename.replace('.ann','').replace('.txt','').replace('.json','')
        if('_data_') in filename2:
            splt =  filename2.replace('@','').split('_data_')
            if len(splt)>1:
                doc_id = splt[1].replace('_', '-')

    text = js.get('text',None)

    is_flood, is_bangladesh, flood_related, flood_climatechange, newspaper, flood_type, anomaly = \
        None, None, None, None, None, None, None
    districts, divisions = [], []
    if 'm_28' in js['metas']: is_flood = js['metas']['m_28']['value']
    if 'm_6' in js['metas']: flood_type = js['metas']['m_6']['value']
    if 'm_30' in js['metas']: newspaper = js['metas']['m_30']['value']
    if 'm_57' in js['metas']: flood_related = js['metas']['m_57']['value']
    if 'm_55' in js['metas']: is_bangladesh = js['metas']['m_55']['value']
    if 'm_33' in js['metas']: flood_climatechange = js['metas']['m_33']['value']
    if 'm_56' in js['metas']: anomaly = js['metas']['m_56']['value']

    for d in ['m_63', 'm_66', 'm_67', 'm_68', 'm_69']:
        if d in js['metas']: districts.append(js['metas'][d]['value'])

    for d in ['m_62', 'm_64', 'm_65']:
        if d in js['metas']: divisions.append(js['metas'][d]['value'])

    dates = []
    if 'm_61' in js['metas']: dates = [d.strip() for d in js['metas']['m_61']['value'].split(',')]
    for entity in js['entities']:
        if entity['classId']=='e_49' or entity['classId']:
            dates.append(extract_dates(entity, debug))

    ans = {
        'doc_id': doc_id,
        'filename': filename,
        'text': text,
        'is_flood': is_flood,
        'is_bangladesh': is_bangladesh,
        'flood_related': flood_related,
        'flood_climatechange': flood_climatechange,
        'newspaper': newspaper,
        'flood_type': flood_type,
        'dates': dates,
        'anomaly': anomaly,
        'districts': districts,
        'divisions': divisions,
    }

    entity_map = {
        'e_15': {
            'name': 'event_damage',
            'entlabel': {
                'f_34': 'crop_damage_area',
                'f_43': 'crop_damage_value',
                'f_44': 'crop_damage_other',
                'f_45': 'damage_info_other',
                'f_35': 'people_affected',
                'f_36': 'peopled_displaced',
                'f_54': 'homes_affected',
                'f_37': 'disease',
                'f_48': 'fatalities'
            }
        },
        'e_49': {
            'name': 'event_dates',
            'entlabel': {
                'f_50': 'date',
                'f_51': 'date',
                'f_60': 'prev_date'
            }
        }
    }
    for entity_val in entity_map.values():
        ans[entity_val['name']] = []
        for entlabel in entity_val['entlabel'].values():
            ans[entity_val['name']+'-'+entlabel] = []
    for entity in js['entities']:
        if entity['classId'] in entity_map:
            e = entity_map[entity['classId']]
            offsets = entity['offsets']
            entry = []
            for off in offsets:
                entry.append({
                    'start': int(off['start']),
                    'end': int(off['start']) + len(off['text'].split(' ')),
                    'text': off['text']
                })
            ans[e['name']].extend(entry)

            if 'fields' in entity:
                entlabel = e['entlabel']
                fields = entity['fields']
                for f in fields:
                    if f in entlabel:
                        entlabelName = e['name'] + '-' + entlabel[f]
                        ans[entlabelName].extend(entry)
    #
    # rel_map = {
    #     'r_59': ['e15', 'e49']
    # }
    # for (rel1, rel2) in rel_map.values():
    #     r1name, r2name = entity_map[rel1]['name'], entity_map[rel2]['name']
    #     relName = r1name + '-rel-' + r2name
    #     ans[relName] = []
    # for relation in js['relations']:
    #     if relation['classId'] in rel_map:
    #         rel1, rel2 = rel_map[relation['classId']]
    #         r1name, r2name = entity_map[rel1]['name'], entity_map[rel2]['name']
    #         relName = r1name + '-rel-' + r2name
    #         entities = relation['entities']

    return ans


def load_data_tagtog(data_folder='data', save_file=None, debug=False):
    if type(data_folder)==str: data_folder = [data_folder]
    elif type(data_folder)==list: data_folder = data_folder
    else: raise Exception('Data Folder type should be str or list')
    columns = ['doc_id', 'filename', 'text', 'is_flood', 'is_bangladesh', 'flood_related', 'flood_climatechange',
               'newspaper', 'flood_type', 'dates', 'anomaly', 'districts', 'divisions', 'event_damage',
               'event_damage-crop_damage_area', 'event_damage-crop_damage_value', 'event_damage-crop_damage_other',
               'event_damage-damage_info_other', 'event_damage-people_affected', 'event_damage-peopled_displaced',
               'event_damage-homes_affected', 'event_damage-disease', 'event_damage-fatalities', 'event_dates',
               'event_dates-date', 'event_dates-prev_date']
    df = pd.DataFrame()
    for fold in data_folder:
        data_files = [f for f in sorted(os.listdir(fold)) if '.json' in f]
        data = [get_data_json(f, fold, debug) for f in data_files]
        df = pd.concat([df, pd.DataFrame(data,columns=columns)])
    if save_file: df.to_csv(save_file)
    return df

def load_data(data_folder='data', balance=None, debug=False):
    if type(data_folder)==str: data_folder = [data_folder]
    elif type(data_folder)==list: data_folder = data_folder
    else: raise Exception('Data Folder type should be str or list')

    df = pd.DataFrame()
    for fold in data_folder:
        if os.path.isfile(fold):
            if '.json' not in fold: raise Exception('Data File must be a json')
            data_files = [fold]
        else:
            data_files = [os.path.join(fold, f) for f in sorted(os.listdir(fold)) if '.json' in f]
        for file in data_files:
            data = json.load(open(file))
            if df is None: df = pd.DataFrame(data)
            else: df = pd.concat([df, pd.DataFrame(data)])
    balance_data, minVal = [], float('inf')
    if balance:
        if balance not in df.columns: raise Exception('Please enter valid column name')
        unique_vals = set(df[balance])
        for u in unique_vals:
            balance_data.append(df.loc[df[balance]==u])
            minVal = min(minVal, len(balance_data[-1]))
        new_df = pd.DataFrame()
        for i,entry in enumerate(balance_data):
            if new_df is None: new_df = entry[:minVal]
            else: new_df = pd.concat([new_df, entry[:minVal]])
        df = new_df
    return df

def remove_cols(df, cols_list):
    for col in cols_list:
        if col in df.columns: df = df.drop([col], axis=1)
    if 'predict' in df.columns and 'is_flood' in df.columns: df = df.drop(['predict'], axis=1)
    if 'text' in df.columns and 'org_text' in df.columns:
        df['text'] = df['org_text']
        df = df.drop(['org_text'], axis=1)
    return df
    
def get_new_predicted_data(prediction_folder='predictions'):
    to_remove_columns = ['abstract', 'news_keywords', 'description', 'keywords', 'dateModified',
                     'link', 'query_info', 'headline', 'authors']
    to_keep_cols = ['datePublished', 'text', 'newspaper', 'doc_id', 'connect_filename', 'is_flood']
    prev_false_data_df, prev_true_data_df = None, None

    is_flood_predicted_file = os.path.join(prediction_folder, 'predicted_isflood.json')
    is_not_flood_predicted_file = os.path.join(prediction_folder, 'predicted_not_isflood.json')
    if os.path.isfile(is_flood_predicted_file):
        js = json.load(open(is_flood_predicted_file))
        prev_true_data_df = pd.DataFrame(js)
        prev_true_data_df = remove_cols(prev_true_data_df, to_remove_columns)
        if 'id' in prev_true_data_df.columns:
            prev_true_data_df['doc_id'] = prev_true_data_df['id']
        if 'connect_filename' not in prev_true_data_df.columns:
            prev_true_data_df['connect_filename'] = ['']*len(prev_true_data_df)
        prev_true_data_df = prev_true_data_df[to_keep_cols]
    if os.path.isfile(is_not_flood_predicted_file):
        js = json.load(open(is_not_flood_predicted_file))
        prev_false_data_df = pd.DataFrame(js)
        prev_false_data_df = remove_cols(prev_false_data_df, to_remove_columns)
        if 'id' in prev_false_data_df.columns:
            prev_false_data_df['doc_id'] = prev_false_data_df['id']
        if 'connect_filename' not in prev_false_data_df.columns:
            prev_false_data_df['connect_filename'] = ['']*len(prev_false_data_df)
        prev_false_data_df = prev_false_data_df[to_keep_cols]
    return prev_true_data_df, prev_false_data_df


def save_data(df_data, save_folder='data'):
    data_true = query_dataframe(df_data, {'is_flood': True})
    data_false = query_dataframe(df_data, {'is_flood': False})

    js = data_true.to_json(orient='records')
    json.dump(json.loads(js), open(os.path.join(save_folder, 'isflood.json'), 'w'), indent=2)

    js = data_false.to_json(orient='records')
    json.dump(json.loads(js), open(os.path.join(save_folder,'not_isflood.json'), 'w'), indent=2)


def make_data_ratio(df_data, test_size=0.2, shuffle_seed=4, debug=False,
                    save_folder=None, load_folder=None, override=False, file_prefix=''):
    from sklearn.model_selection import train_test_split
    save_file, load_file = None, None
    if save_folder: save_file = os.path.join(save_folder, file_prefix + 'data.json')
    if load_folder: load_file = os.path.join(load_folder, file_prefix + 'data.json')

    if not override and load_file and os.path.isfile(load_file):
        if debug: print('loaded', load_file)
        js = json.load(open(load_file))
        train_df = pd.DataFrame(js['train'])
        test_df = pd.DataFrame(js['test'])
        return {'train': train_df, 'test': test_df}

    true_data = df_data.loc[df_data['is_flood'] == True]
    false_data = df_data.loc[df_data['is_flood'] == False]
    train_true, test_true = train_test_split(true_data, test_size=test_size, random_state=shuffle_seed)
    train_false, test_false = train_test_split(false_data, test_size=test_size, random_state=shuffle_seed)

    train_df = pd.concat([train_true, train_false])
    train_df = train_df.sample(n=len(train_df), random_state=shuffle_seed).reset_index(drop=True)
    test_df = pd.concat([test_true, test_false])
    test_df = test_df.sample(n=len(test_df), random_state=shuffle_seed).reset_index(drop=True)

    if debug: print('Data Loaded')

    if save_file:
        train_json = train_df.to_json(orient='records')
        test_json = test_df.to_json(orient='records')
        json.dump({'train': json.loads(train_json), 'test': json.loads(test_json)}, open(save_file, 'w'), indent=2)
    return {'train': train_df, 'test': test_df}

def query_dataframe(df, d, debug=False):
    df2 = df.copy()
    for key, val in d.items(): df2 = df2.loc[df2[key] == val]
    return df2

# Add different cols to data
def add_newspapers(df_data):
    newspapers = []
    for row in df_data.iterrows():
        try:
            doc_id = row[1]['doc_id']
            filename = row[1]['filename']
            newspaper = row[1]['newspaper']
            new_newspaper = None
            if not doc_id: new_newspaper = 'nytimes'
            else:
                if filename: new_newspaper = make_newspaper_filename(filename)
                elif newspaper: new_newspaper = newspaper
            newspapers.append(new_newspaper)
        except Exception as e:
            print(e, row[1]['doc_id'], row[1]['filename'],row[1]['newspaper'])
            newspapers.append(None)
            continue
    df_data['newspaper'] = newspapers
    df_data = df_data[df_data['newspaper'].astype(bool)]
    return df_data

def add_datePublished(df_data):
    datePublished = []
    for row in df_data.iterrows():
        newspaper = row[1]['newspaper']
        doc_id = row[1]['doc_id']
        filename = row[1].get('filename',None)
        try:
            if newspaper:
                datePublished.append(get_id_data(newspaper, query_id=doc_id, connect_filename=filename,
                                                            query_term='datePublished'))
            else: datePublished.append(None)
        except Exception as e:
            print(e, doc_id, )
            datePublished.append(None)
            continue
    df_data['datePublished'] = datePublished
    df_data = df_data[df_data['datePublished'].astype(bool)].fillna('')
    return df_data

def get_dist_divD():
    under_division = json.load(open('timeseries_data/logistics/under_division.json'))
    dist_to_div = {}
    for k,v in under_division.items():
        for dis in v:
            dist_to_div[dis.lower()] = k.lower()
    to_add = {'nawabganj': 'rajshahi', "cox's bazar": 'chattogram', 'netrakona': 'dhaka', 'bogra': 'rajshahi', 'barisal': 'barishal', 'jessore': 'khulna', 'brahamanbaria': 'chattogram', 'chittagong': 'chattogram', 'comilla': 'chattogram', 'jhalokati': 'barishal', 'maulvibazar': 'sylhet'}
    for k,v in to_add.items():
        dist_to_div[k]=v

    return under_division, dist_to_div

def add_location(df_data):
    div_to_dist, dist_to_div= get_dist_divD()
    divisions_list = set(div_to_dist.keys())
    for d in ["barisal","chittagong"]: divisions_list.add(d)
    div_map = {'barisal':"barishal", "chittagong":"chattogram"}
    districts_list = set(dist_to_div.keys())
    districts, divisions = [], []
    unique_dists, unique_divisions = set(),set()
    for row in df_data.iterrows():
        try:
            text = row[1]['text']
            dist, divs = set(), set()
            for d in districts_list:
                if d.lower()=='dhaka':
                    if re.search("dhaka (?!tribune)", text.lower()):
                        dist.add('dhaka')
                elif d.lower() in text.lower():
                    dist.add(d.lower())
                    divs.add(dist_to_div[d.lower()])
            for d in divisions_list:
                if d.lower()=='dhaka':
                    if re.search("dhaka (?!tribune)", text.lower()):
                        divs.add('dhaka')
                elif d.lower() in text.lower(): divs.add(div_map.get(d.lower(),d.lower()))
            districts.append(list(dist))
            divisions.append(list(divs))
        except Exception as e:
            print(e, row[1]['doc_id'], row[1]['newspaper'])
            districts.append([])
            divisions.append([])
    df_data['districts'], df_data['divisions'] = districts, divisions
    df_data = df_data.fillna('')
    return df_data


# Add previous true data
def add_prev_true_data(df_data):
    prev_true_data_df, prev_false_data_df = get_new_predicted_data()
    if prev_true_data_df is not None: df_data = pd.concat([df_data, prev_true_data_df])
    df_data = df_data.fillna('')
    return df_data


from datetime import datetime
import dateparser

def parse_date(date):
    dp = dateparser.parse(date, settings={'RELATIVE_BASE': datetime(1400, 1, 1)})
    if dp:
        if dp.year==1400: raise Exception('No Year Present')
        year = dp.year
        if year > 2021:
            raise Exception('No Date Present', date)
        month=dp.month
        day = dp.day
        if dp.month==1 and dp.day==1:
            month, day=None, None
        return {'year': year, 'month':month, 'day':dp.day}
    else:
        raise Exception('No Date Present', date)

def parse_all_dates(dates_all):
    dates = []
    for d in dates_all:
        if type(d)==list:
            for dd in d:
                try:
                    if dd: dates.append(parse_date(dd))
                except Exception as e:
                    dates.append(None)
                    print(e, d)
                    continue
        else:
            try:
                dates.append(parse_date(d))
            except Exception as e:
                dates.append(None)
                print(e, d)
                continue
    return dates

from collections import defaultdict
def date_counts(date_dict):
    year_count, year_month_count, year_month_day_count = defaultdict(int), defaultdict(int), defaultdict(int)
    for d in date_dict:
        if d:
            year_count[str(d['year'])] += 1
            if 'month' in d and d['month']: year_month_count[str(d['year']) + '-' + str(d['month'])] += 1
            if 'month' in d and d['month'] and 'day' in d and d['day']: year_month_day_count[
                str(d['year']) + '-' + str(d['month']) + '-' + str(d['day'])] += 1
    year_count_list = [(k, v) for k, v in year_count.items()]
    year_month_count_list = [(k, v) for k, v in year_month_count.items()]
    year_month_day_count_list = [(k, v) for k, v in year_month_day_count.items()]
    year_count_list.sort(key=lambda x: int(x[0]))
    year_month_count_list.sort(key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])))
    year_month_day_count_list.sort(
        key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1]), int(x[0].split('-')[2])))

    return year_count_list, year_month_count_list, year_month_day_count_list


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


def complete_day(list1, year_range=[2015, None], aggType=None, normDict=None, normAgg='month', ignoreDates = {}):
    dict1_year_months_day = {i[0]: i[1] for i in list1}
    all_years = set([int(i.split('-')[0]) for i in dict1_year_months_day.keys()])

    min_year, max_year = min(all_years), max(all_years)
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = range(min_range, max_range+1)

    d1_year_month_day = []
    for i in all_years:
        count = 0
        innerMonth = []
        monthRange = 13
        if i == 2020: monthRange = 10
        for months in range(1, monthRange):
            if int(i) in ignoreDates:
                if int(months) in ignoreDates[int(i)]: continue
            day_range = 31 if months in [1, 3, 5, 7, 8, 10, 12] else 30
            if months == 2:
                if isLeap(i): day_range = 29
                else: day_range = 28
            toAdd = 0
            normFactor = [0,0]
            normFactorAv = [0,0]
            innerArr = []
            normArr = []
            for day in range(1, day_range + 1):
                key = str(i) + '-' + str(months) + '-' + str(day)
                toAdd += dict1_year_months_day.get(key, 0)
                if normDict is not None:
                    normFactor[0] += normDict.get(key, 0)
                    normFactor[1] += 1
                    count += normDict.get(key, 0)
                    normFactorAv[0] += normDict.get(key, 0)
                    normFactorAv[1] += 1
                if normDict is not None and (normAgg == 'week' and day % 7 == 0) \
                    or (normAgg == 'fortnight' and day % 15 == 0) or (type(normAgg)==int and day % normAgg==0):
                    if normFactor[0] == 0:
                        print('Norm Factor = 0', key)
                        if normFactorAv[0] == 0:
                            print('Norm Factor Av = 0', key)
                        else:
                            normArr.append(normFactorAv[0] / normFactorAv[1])
                    else:
                        normArr.append(normFactor[0]/normFactor[1])
                    normFactor = [0,0]
                if (aggType is None) or (aggType == 'week' and day % 7 == 0) \
                    or (aggType == 'fortnight' and day % 15 == 0) or (type(aggType)==int and day % aggType==0) \
                    or (day == day_range and aggType != 'month'):
                    innerArr.append((key, toAdd))
                    toAdd = 0
            if (aggType == 'month'):
                key = str(i) + '-' + str(months)
                innerArr.append((key, toAdd))
            if normDict is not None:
                key = str(i) + '-' + str(months)
                if normAgg == 'month':
                    if normFactorAv[0] == 0:
                        print('Norm Factor Av = 0', key)
                    else:
                        innerArr = [(k,n/normFactorAv[0]) for k,n in innerArr]
                elif normAgg == 'week' or normAgg == 'fortnight':
                    assert len(normArr) == len(innerArr)
                    for i in range(len(innerArr)):
                        normFac = normArr[i]
                        innerArr[i][1] /= normFac
            innerMonth.extend(innerArr)
        if aggType == 'year':
            innerMonth = [(str(i), sum([j[1] for j in innerMonth]))]
        if normAgg == 'year':
            innerMonth = [(k,n/count) for k,n in innerMonth]
        d1_year_month_day.extend(innerMonth)

    l1 = sorted(d1_year_month_day, key=lambda x: tuple(map(int, x[0].split('-'))))
    return l1


def load_year(d, year_range=[None, None]):
    d = {int(k): v for k, v in d.items()}
    all_years = set(d.keys())
    min_year, max_year = min(all_years), max(all_years)
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = sorted([y for y in all_years if min_range <= y <= max_range])
    d_years = {k: d.get(k, 0) for k in all_years}
    years = [(int(k), float(v)) for k, v in d_years.items()]
    years.sort(key=lambda x: int(x[0]))
    return years


def load_year_month(d, year_range=[None, None], ignoreDates={}):
    # year_month = [(k,float(v)) for k,v in d.items()]
    all_years = set([int(i.split('-')[0]) for i in d.keys()])
    min_year, max_year = min(all_years), max(all_years)
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = sorted([y for y in all_years if min_range <= y <= max_range])
    year_months = [str(i) + '-' + str(count) for i in all_years for count in range(1, 13)
                   if (i not in ignoreDates) or (i in ignoreDates and count not in ignoreDates[i])]
    d_year_month = {k: d.get(k, 0) for k in year_months}
    year_month_list = sorted([(k, v) for k, v in d_year_month.items()],
                             key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])))

    return year_month_list


def match_years(list1, list2, match_type='add', complete=False):
    match_type = match_type.lower()
    l1 = set([int(i[0]) for i in list1])
    l2 = set([int(i[0]) for i in list2])
    if match_type == 'add':
        ls1 = list1 + [(i, 0) for i in l2 - l1]
        ls2 = list2 + [(i, 0) for i in l1 - l2]
    elif match_type == 'remove':
        not_present1, not_present2 = l2 - l1, l1 - l2
        ls1 = [i for i in list1 if i[0] not in not_present2]
        ls2 = [i for i in list2 if i[0] not in not_present1]
    else:
        raise Exception('match_type should be add or remove')

    if complete:
        l1 = [int(i[0]) for i in ls1]
        l2 = [int(i[0]) for i in ls2]
        min_year = min(l1 + l2)
        max_year = max(l1 + l2)
        ls1 += [(i, 0) for i in range(min_year, max_year + 1) if i not in l1]
        ls2 += [(i, 0) for i in range(min_year, max_year + 1) if i not in l2]
    return sorted(ls1, key=lambda x: int(x[0])), sorted(ls2, key=lambda x: int(x[0]))


def match_years_months(list1, list2, year_range=[2017, None]):
    dict1_year_months = {i[0]: i[1] for i in list1}
    dict2_year_months = {i[0]: i[1] for i in list2}

    set1_years = set([int(i.split('-')[0]) for i in dict1_year_months.keys()])
    set2_years = set([int(i.split('-')[0]) for i in dict2_year_months.keys()])
    all_years = set1_years.union(set2_years)

    min_year, max_year = min(all_years), max(all_years)
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = sorted([y for y in all_years if min_range <= y <= max_range])

    list1_year_months = [str(i) + '-' + str(count) for i in all_years for count in range(1, 13)]
    list2_year_months = [str(i) + '-' + str(count) for i in all_years for count in range(1, 13)]
    d1_year_month = {k: dict1_year_months.get(k, 0) for k in list1_year_months}
    d2_year_month = {k: dict2_year_months.get(k, 0) for k in list2_year_months}
    l1 = sorted([(k, v) for k, v in d1_year_month.items()],
                key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])))
    l2 = sorted([(k, v) for k, v in d2_year_month.items()],
                key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])))
    return l1, l2


def get_month_range(list1, year_range = [2017, None]):
    dict1_year_months = {i[0]:i[1] for i in list1}
    set1_years = set([int(i.split('-')[0]) for i in dict1_year_months.keys()])
    all_years = set1_years
    if all_years: min_year, max_year = min(all_years), max(all_years)
    else: min_year, max_year = 2017, 2020
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = [y for y in range(min_range, max_range+1)]
    list1_year_months = [str(i)+'-'+str(count) for i in all_years for count in range(1,13)]
    d1_year_month = {k:dict1_year_months.get(k, 0) for k in list1_year_months}
    l1 = sorted([(k,v) for k,v in d1_year_month.items()],
                key=lambda x:(int(x[0].split('-')[0]), int(x[0].split('-')[1])))
    return l1


def plot_timeseries(l, title='', xlabel='', ylabel='', xticks_rotate=False, skip=0):
    plt.figure(figsize=(15, 7))
    colors = ['b', 'r', 'g', 'c','m','y','k','w']
    for i, entry in enumerate(l):
        plot_color = entry.get('color', colors[i])
        if entry.get('type', None) == 'bar':
            plt.bar([i[0] for i in entry['count_list']], [i[1] for i in entry['count_list']],
                    color=plot_color, label=entry['label'])
        else:
            plt.plot([i[0] for i in entry['count_list']], [i[1] for i in entry['count_list']],
                     linestyle='-', marker='o', color=plot_color, label=entry['label'])
        plt.xticks([i[0] for i in entry['count_list']])

    plt.legend(fontsize=18)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if xticks_rotate: plt.xticks(rotation='vertical')

    if skip:
        ax = plt.gca()
        temp = ax.xaxis.get_ticklabels()
        temp = list(set(temp) - set(temp[::skip]))
        for label in temp:
            label.set_visible(False)
    plt.show()

def calculate_ylim(y_data):
    minVal, maxVal, total = min(y_data), max(y_data), len(y_data)
    add_factor = np.std(y_data)
    return minVal, maxVal + add_factor


def plot_2timeseries(l1, l2, title='', xlabel='', xticks_rotate=False, skip=0, plt_args={},
                     xticksFontSize=16, yticksFontSize=16, xLabelFontSize=16, ylabelFontSize=16, 
                     sameY=False, yline=None, save_path=None, year_range=[2017,2020]):
    xticksFontSize=plt_args.get('xticksFontSize',28)
    yticksFontSize=plt_args.get('yticksFontSize',28)
    xlabelFontSize=plt_args.get('xlabelFontSize',28)
    ylabelFontSize=plt_args.get('ylabelFontSize',28)
    titleFontSize=plt_args.get('titleFontSize',28)
    legendFontSize=plt_args.get('legendFontSize',28)
    figSize=plt_args.get('figSize',(15,7))
    
    plt.figure(figsize=figSize)

    # l1
    fig, ax1 = plt.subplots(figsize=figSize)
    plot_color = l1.get('color', 'r')
    if l1.get('type', None) == 'bar':
        ax1.bar([i[0] for i in l1['count_list']], [i[1] for i in l1['count_list']],
                color=plot_color, label=l1['label'])
    else:
        ax1.plot([i[0] for i in l1['count_list']], [i[1] for i in l1['count_list']],
                 linestyle='-', marker='x', color=plot_color, label=l1['label'], markersize=10)
    ax1.set_xlabel(xlabel, fontsize=xlabelFontSize)
    ax1.set_ylabel(l1.get('ylabel', ''), color=plot_color, fontsize=ylabelFontSize)
    ax1.tick_params(axis='y', labelcolor=plot_color, labelsize=yticksFontSize)
    ax1.tick_params(axis='x', labelrotation=90 if xticks_rotate else None, labelsize=xticksFontSize)
    ax1.legend(fontsize=legendFontSize, loc='upper left')
    x1minVal, x1maxVal = calculate_ylim([i[1] for i in l1['count_list']])
    ylim_min, ylim_max = l1.get('ylim_min', x1minVal), l1.get('ylim_max', x1maxVal)
    ax1.set_ylim(ylim_min, ylim_max)

    # l2
    ax2 = ax1.twinx()
    plot_color = l2.get('color', 'b')
    if l2.get('type', None) == 'bar':
        ax2.bar([i[0] for i in l2['count_list']], [i[1] for i in l2['count_list']],
                color=plot_color, label=l1['label'])
    else:
        ax2.plot([i[0] for i in l2['count_list']], [i[1] for i in l2['count_list']],
                 linestyle='-', marker='o', color=plot_color, label=l2['label'])
    ax2.set_xlabel(xlabel, fontsize=xlabelFontSize)
    ax2.set_ylabel(l2.get('ylabel', ''), color=plot_color, fontsize=ylabelFontSize)
    ax2.tick_params(axis='y', labelcolor=plot_color, labelsize=yticksFontSize)
    ax2.tick_params(axis='x', labelrotation=90 if xticks_rotate else None, labelsize=xticksFontSize)
    ax2.legend(fontsize=legendFontSize, loc='upper right')
    x2minVal, x2maxVal = calculate_ylim([i[1] for i in l2['count_list']])
    ylim_min, ylim_max = l1.get('ylim_min', x2minVal), l1.get('ylim_max', x2maxVal)
    ax2.set_ylim(ylim_min, ylim_max)
    
    if sameY:
        minVal, maxVal = min(x1minVal, x2minVal), max(x1maxVal,x2maxVal)
        ax1.set_ylim(minVal, maxVal)
        ax2.set_yticks([])
#         ax2.set_ylim(minVal, maxVal)
            

    plt.xticks([i[0] for i in l2['count_list']])
    

    fig.suptitle(title, fontsize=titleFontSize, y=title.count('\n') * .05 + 1.02)
    #     if xticks_rotate: fig.xticks(rotation='vertical')
    if skip:
        temp = ax1.xaxis.get_ticklabels()
        temp = list(set(temp) - set(temp[::skip]))
        for label in temp:
            label.set_visible(False)
    
    xt = []
    for i in range(year_range[0],year_range[1]+1): xt.extend([str(i)]*12)
    ax1.set_xticklabels(xt)
    
    if yline:
        plt.axhline(yline)
        plt.text(len(l1['count_list'])-0.75, yline+(yline/16), '{}'.format(yline) )
    fig.tight_layout()
    if save_path: plt.savefig(save_path, dpi=128)
    plt.show()

def subPlotN(ls, title='', xlabel='', xticks_rotate=False, skip=0, xticksFontSize=14):
    fig, axs = plt.subplots(len(ls),1, figsize=(10,len(ls)*3))
    fig.subplots_adjust(hspace = 0.01, wspace=0)
    
    for i in range(len(ls)):
        ll = ls[i]
        plot_color = ls[i].get('color', 'r')
        if ll.get('type', None) == 'bar':
            axs[i].bar([i[0] for i in ll['count_list']], [i[1] for i in ll['count_list']],
                    color=plot_color, label=ll['label'])
        else:
            axs[i].plot([i[0] for i in ll['count_list']], [i[1] for i in ll['count_list']],
                     linestyle='-', marker='o', color=plot_color, label=ll['label'])
            
        axs[i].set_ylabel(ll.get('ylabel', ''), color=plot_color, fontsize=14)
        axs[i].tick_params(axis='y', labelcolor=plot_color, labelsize=14)
        axs[i].legend(fontsize=14, loc='upper left')
        minVal, maxVal = calculate_ylim([i[1] for i in ll['count_list']])
        axs[i].set_ylim(minVal, maxVal)
        if i!=len(ls)-1: plt.setp(axs[i].get_xticklabels(), visible=False)
    
    plt.tick_params(axis='x', labelrotation=90 if xticks_rotate else None, labelsize=xticksFontSize)
    fig.suptitle(title, fontsize=16, y=title.count('\n') * .02 + 1.02)
    if skip:
        ax = plt.gca()
        temp = ax.xaxis.get_ticklabels()
        temp = list(set(temp) - set(temp[::skip]))
        for label in temp:
            label.set_visible(False)
    fig.tight_layout()
    plt.show()
    
def aggregate_data_month(dates_vals, aggregate_func=max, ignoreDates={}):
    dates_vals = [(dateparser.parse(i[0]), i[1]) for i in dates_vals]
    month_vals = defaultdict(float)
    for (date, val) in dates_vals:
        year, month = date.year, date.month
        year_month_str = '{}-{}'.format(year, month)
        month_vals[year_month_str] = aggregate_func(month_vals[year_month_str],val)
    return load_year_month(month_vals, ignoreDates=ignoreDates)

def get_Sentinel1_data_monthly(division, agg_func=max, div_factor=1000000, ignoreDates={}):
    folderpath_s1 = 'other_data/Sentinel1_ts'
    files_s1 = [f for f in os.listdir(folderpath_s1) if '.csv' in f]
    s1_df = None
    if division == 'all':
        s1_df = pd.read_csv(os.path.join(folderpath_s1, 'Bangladesh-fulldata-2017-2020.csv'))
        s1_df_list = [(row[1]['Dates'], row[1]['country Flooded Area (m^2)']/div_factor) for row in s1_df.iterrows()]
    else:
        for filepath in files_s1:
            if division.lower() not in filepath.lower(): continue
            temp_df = pd.read_csv(os.path.join(folderpath_s1, filepath))
            if s1_df is None: s1_df = temp_df
            else: s1_df = pd.concat([s1_df,temp_df])
        s1_df_list = [(row[1]['Dates'], row[1]['division Flooded Area (m^2)']/div_factor) for row in s1_df.iterrows()]
    s1_month_count_list = aggregate_data_month(s1_df_list, aggregate_func=agg_func, ignoreDates=ignoreDates)
    return s1_month_count_list

def get_PMW_data_monthly(division, agg_func=max, ignoreDates={}):
    folderpath_pmw_flood = 'other_data/pmw_flood_ts'
    files_pmw_flood = [f for f in os.listdir(folderpath_pmw_flood) if '.csv' in f]
    pmw_flood_df = None
    for filepath in files_pmw_flood:
        if division.lower() not in filepath.lower(): continue
        temp_df = pd.read_csv(os.path.join(folderpath_pmw_flood, filepath))
        if pmw_flood_df is None: pmw_flood_df = temp_df
        else: pmw_flood_df = pd.concat([pmw_flood_df,temp_df])

    pmw_flood_fraction_df_list = [(row[1]['Date'], row[1]['Fraction of District Flooded']) for row in pmw_flood_df.iterrows()]
    pmw_flood_fraction_month_count_list = aggregate_data_month(pmw_flood_fraction_df_list, 
                                                               aggregate_func=agg_func, ignoreDates=ignoreDates)
    return pmw_flood_fraction_month_count_list


def complete_day_loc(list1, year_range = [2015, None], aggType=None, onlyUnique=False, returnLoc=False):
    dict1_year_months_day = {i[0]:i[1] for i in list1}
    all_years = set([int(i.split('-')[0]) for i in dict1_year_months_day.keys()])
    
    min_year, max_year = min(all_years), max(all_years)
    min_range = year_range[0] if year_range[0] is not None else min_year
    max_range = year_range[1] if year_range[1] is not None else max_year
    all_years = range(min_range, max_range+1)
    
    d1_year_month_day = []
    d1_year_month_day_loc = []
    for i in all_years:
        count = 0
        monthRange = 13
        if i == 2020: monthRange = 10
        for months in range(1,monthRange):
            day_range = 31 if months in [1,3,5,7,8,10,12] else 30
            if months==2:
                if isLeap(i): day_range = 29
                else: day_range = 28
            toAdd = 0
            toAddSet = set()
            for day in range(1, day_range+1):
                key = str(i)+'-'+str(months)+'-'+str(day)
                val = dict1_year_months_day.get(key, set())
                if onlyUnique:
                    toAddSet = toAddSet.union(val)
                    toAdd = len(toAddSet)
                else: toAdd += len(val)
                if (aggType is None) or (aggType=='week' and day%7==0) \
                or (aggType=='fortnight' and day%15==0) or (day == day_range and aggType!='month'):
                    d1_year_month_day.append((key,toAdd))
                    if returnLoc: d1_year_month_day_loc.append((key, toAddSet))
                    toAdd,toAddSet = 0, set()
                count += 1
            if (aggType=='month'):
                key = str(i)+'-'+str(months)
                if onlyUnique:
                    toAdd = len(toAddSet)
                d1_year_month_day.append((key,toAdd))
                if returnLoc: d1_year_month_day_loc.append((key, toAddSet))

    l1 = sorted(d1_year_month_day, key=lambda x:tuple(map(int, x[0].split('-'))))
    l2 = sorted(d1_year_month_day_loc, key=lambda x:tuple(map(int, x[0].split('-'))))
    if returnLoc: return l1,l2
    return l1

if __name__=='__main__':
    df = load_data_tagtog('data')
    print(df)

    # print(len(df.loc[df['is_flood']==True])
