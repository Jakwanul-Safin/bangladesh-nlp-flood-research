import os
import pandas as pd
import json
from sklearn import model_selection

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

    return {
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
        'divisions': divisions
    }


def load_data_tagtog(data_folder='data', save_file=None, debug=False):
    if type(data_folder)==str: data_folder = [data_folder]
    elif type(data_folder)==list: data_folder = data_folder
    else: raise Exception('Data Folder type should be str or list')
    columns = ['doc_id', 'filename', 'is_flood', 'is_bangladesh', 'flood_related', 'flood_climatechange',
               'newspaper', 'flood_type', 'text', 'dates', 'anomaly', 'districts', 'divisions']
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
    prev_false_data_df, prev_true_data_df = None, None

    is_flood_predicted_file = os.path.join(prediction_folder, 'predicted_isflood.json')
    is_not_flood_predicted_file = os.path.join(prediction_folder, 'predicted_not_isflood.json')
    if os.path.isfile(is_flood_predicted_file):
        js = json.load(open(is_flood_predicted_file))
        prev_true_data_df = pd.DataFrame(js)
        prev_true_data_df = remove_cols(prev_true_data_df, to_remove_columns)
        prev_true_data_df.columns = ['datePublished', 'text', 'doc_id', 'connect_filename', 'newspaper', 'is_flood']
    if os.path.isfile(is_not_flood_predicted_file):
        js = json.load(open(is_not_flood_predicted_file))
        prev_false_data_df = pd.DataFrame(js)
        prev_false_data_df = remove_cols(prev_false_data_df, to_remove_columns)
        prev_false_data_df.columns = ['datePublished', 'text', 'doc_id', 'connect_filename', 'newspaper', 'is_flood']
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


if __name__=='__main__':
    df = load_data_tagtog('data2')
    print(df)

    # print(len(df.loc[df['is_flood']==True])
