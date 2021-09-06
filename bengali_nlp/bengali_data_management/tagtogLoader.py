import os
import json, re, pandas as pd
from bs4 import BeautifulSoup

class TagtogLoader:
    def __init__(self, folder):
        self.root = folder
        self.pool = os.path.join(self.root, "plain.html", "pool")
        self.ann = os.path.join(self.root, "ann.json")
        
        with open(os.path.join(self.root, "annotations-legend.json"), 'r') as f:
            self.annotations_key = json.load(f)
            
    def load_text(self):
        self.files = {}
        
        folders = os.listdir(self.pool)
        if len(folders) != 1:
            raise FileNotFoundError(f"Expecting exactly one folder within pool, found {len(folders)}")
        
        for name in os.listdir(os.path.join(self.pool, folders[0])):
            with open(os.path.join(self.pool, folders[0], name), 'r') as f:
                name = '.'.join(name.split(".")[:-3])
                self.files[name] = BeautifulSoup(f.read(), features="html.parser").find('div', class_='content').text
        
        return self.files
    
    def load_annotations(self, who = "shammun"):
        self.annotations = {}
        if who == "master" or None:
            where = os.path.join(self.ann, "master", "pool")
        else:
            where = os.path.join(self.ann, "members", who, "pool")
        
        if not os.path.exists(where):
            raise FileNotFoundError(f"Annotions by {who} not found in {where}")
        
        folders = os.listdir(where)
        if len(folders) != 1:
            raise FileNotFoundError(f"Expecting exactly one folder within pool, found {len(folders)}")
        
        for name in os.listdir(os.path.join(where, folders[0])):
            with open(os.path.join(where, folders[0], name), 'r') as f:
                name = '.'.join(name.split(".")[:-3])
                self.annotations[name] = {self.annotations_key[k]: v['value'] 
                                          for k, v in json.load(f)["metas"].items() 
                                          if k in self.annotations_key
                                         }
        
        print(len(self.annotations), " annotations found")
        return self.annotations
    
    def attach_content_from_file(self):
        for k, v in self.files.items():
            if k in self.annotations:
                self.annotations[k]['content'] = v

    def attach_matching_csv(self, csv):
        decodeKey = re.compile("^([^-]*)-([^-.]*\.csv)_(\d+)$")

        for k, info in self.annotations:
            hashkey, matching_csv, index = decodeKey.match(k).groups()
            index = int(index)

            match_df = pd.read_csv(csv, index_col=0)

            formated_content = match_df.iloc[index-1][0]
            components = formated_content.split("\n")
            index, title, date, headline = components[:4]
            if 'http' in components[-1]:
                content = components[4:-1]
                link = components[-1]
            else:
                content = components[4:]
            content = "\n".join(content)

    def dataframe(self):
        return pd.DataFrame(list(self.annotations.values()))

def load_generator(annotations_folder, csv_folder = ""):
    decodeFilename = re.compile("^([^-]*)-([^-.]*\.csv)_(\d+)\.ann\.json$")
    loaded_df = {}
    
    for fname in os.listdir(annotations_folder):
        hashkey, matching_csv, index = decodeFilename.match(fname).groups()
        index = int(index)
        if matching_csv not in loaded_df:
            loaded_df[matching_csv] = pd.read_csv(os.path.join(csv_folder, matching_csv), index_col=0)
        formated_content = loaded_df[matching_csv].iloc[index-1][0]
        components = formated_content.split("\n")
        index, title, date, headline = components[:4]
        if 'http' in components[-1]:
            content = components[4:-1]
            link = components[-1]
        else:
            content = components[4:]
        content = "\n".join(content)
        
        with open(os.path.join(annotations_folder, fname), 'r') as f:
            is_flood = json.load(f)['metas']['m_28']['value']
        
        yield {'index': index,
         'title': title,
         'date': date,
         'headline': headline,
         'content': content,
         'is_flood': is_flood
        }

def load_from_annotations_folder(annotations_folder, csv_folder = ""):
    df = pd.DataFrame(list(load_generator(annotations_folder, csv_folder=csv_folder)))
    df.set_index('index')
    return df