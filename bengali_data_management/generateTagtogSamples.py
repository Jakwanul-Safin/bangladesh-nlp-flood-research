from abc import abstractclassmethod
import sys, os
sys.path.insert(0, '..')

import pandas as pd
import json

from basicBanglaTools import *
from data_management_tools import *

from abc import ABC, abstractclassmethod

DATA_FOLDER = "data_for_samples"
FORMATED_SAMPLE_FOLDER = os.path.join("samples", "formated")
UNFORMATED_SAMPLE_FOLDER = os.path.join("samples", "unformated")

class Sample(ABC):

    @abstractclassmethod
    def generate(self, indentifiers_for_everysample):
        raise NotImplementedError

    @abstractclassmethod
    def unformated_output_file(self):
        raise NotImplementedError

    @abstractclassmethod
    def formated_output_file(self):
        raise NotImplementedError

    def save(self):
        if os.path.exists(self.unformated_output_file()):
            loaded = pd.read_csv(self.unformated_output_file(), index_col=0)
            assert( (loaded == self.tagtog_sample).all().all() )
        else:
            self.tagtog_sample.to_csv(self.unformated_output_file())

        if os.path.exists(self.formated_output_file()):
            loaded = pd.read_csv(self.formated_output_file(), index_col = 0, squeeze = True)
            assert((loaded == self.formated_sample).all())
        else:
            self.formated_sample.to_csv(self.formated_output_file())

class BengaliArticlesSample1(Sample):
    def __init__(self):
        self.tagtog_sample = None
        self.formated_sample = None

    def generate(self, indentifiers_for_everysample):
        if self.tagtog_sample is not None and self.formated_sample is not None:
            return self.tagtog_sample, self.formated_sample

        df = pd.read_csv(os.path.join(DATA_FOLDER, "serpFullArticlesScrapeSample.csv"), delimiter = "\t")
        self.tagtog_sample = df.groupby('paper', group_keys=False).apply(lambda x: x.sample(min(len(x), 8), random_state=42))
        self.formated_sample = self.tagtog_sample.apply(lambda x: "\n".join([str(x.name), x.title.replace("\n", ""), x.date.replace("\n", ""), x.headline.replace("\n", ""), x.content]), axis=1)
        indentifiers_for_everysample['bengali_articles_sample1'] = set(self.tagtog_sample['link'])

        return self.tagtog_sample, self.formated_sample

    def unformated_output_file(self):
        return os.path.join(UNFORMATED_SAMPLE_FOLDER, "Unformated_6_9_2021_tagtogsample.csv")
    
    def formated_output_file(self):
        return os.path.join(FORMATED_SAMPLE_FOLDER, "6_9_2021_tagtogsample.csv")

class BengaliFloodKeywords(Sample):
    def __init__(self):
        self.tagtog_sample = None
        self.formated_sample = None

    def hasWordsFilter(self, words):
        return lambda text: any(word in text for word in words)

    def generate(self, indentifiers_for_everysample):
        if self.tagtog_sample is not None and self.formated_sample is not None:
            return self.tagtog_sample, self.formated_sample

        df = pd.read_csv(os.path.join(DATA_FOLDER, "serpFullArticlesScrapeSample.csv"), delimiter = "\t")
        keyword_df = df[df['content'].apply(self.hasWordsFilter(["জলমগ্ন","জোয়ারের", "প্লাবিত" ,"বন্যা", "জলাবদ্ধতা", "উজান", "ঘূর্ণিঝড়","নদী","ভাঙ্গন"]))]
        self.tagtog_sample = keyword_df.groupby('paper', group_keys=False).apply(lambda x: x.sample(min(len(x), 8), random_state=42))
        self.formated_sample = self.tagtog_sample.apply(lambda x: "\n".join([str(x.name), x.title.replace("\n", ""), x.date.replace("\n", ""), x.headline.replace("\n", ""), x.content]), axis=1)

        indentifiers_for_everysample['has_flood_keywords'] = set(self.tagtog_sample['link'])

        return self.tagtog_sample, self.formated_sample

    def formated_output_file(self):
        return os.path.join(FORMATED_SAMPLE_FOLDER, "6_9_2021_tagtogkeywordsample.csv")
    
    def unformated_output_file(self):
        return os.path.join(UNFORMATED_SAMPLE_FOLDER, "Unformated_6_9_2021_tagtogkeywordsample.csv")

class ProthomAlo(Sample):
    def __init__(self):
        self.tagtog_sample = None
        self.formated_sample = None

    def generate(self, indentifiers_for_everysample):
        if self.tagtog_sample is not None and self.formated_sample is not None:
            return self.tagtog_sample, self.formated_sample

        with open(os.path.join(DATA_FOLDER, "prothom_alo_articlescrapes_bengali.json"), 'r') as f:
            df = pd.DataFrame(json.load(f))
            
        with open(os.path.join(DATA_FOLDER, 'prothom_alo_webscrapes_topicবন্যা.json'), 'r') as f:
            topic_pages = pd.DataFrame(json.load(f))
            
        flood_articles = df.join(topic_pages[['link']].set_index('link'), on="link", how="inner")

        # Ensures flood articles are not too small or empty
        flood_articles = flood_articles[flood_articles['content'].apply(len) > 200]

        # Ensures flood articles were not in a prior sample
        self.tagtog_sample = flood_articles[flood_articles['link'].apply(lambda link: all(link not in sample for sample in indentifiers_for_everysample.values()))]
        self.formated_sample = self.tagtog_sample.apply(lambda x: "\n".join([str(x.name), x.title.replace("\n", ""), x.date.replace("\n", ""), x.headline.replace("\n", ""), x.content]), axis=1)

        indentifiers_for_everysample['prothom_alo_topic'] = set(self.tagtog_sample['link'])
        return self.tagtog_sample, self.formated_sample

    def formated_output_file(self):
        return os.path.join(FORMATED_SAMPLE_FOLDER, "6_17_2021_flood_topic_articles.csv")
    
    def unformated_output_file(self):
        return os.path.join(UNFORMATED_SAMPLE_FOLDER, "Unformated_6_17_2021_flood_topic_articles.csv")

class KeywordStratified(Sample):
    def __init__(self):
        self.tagtog_sample = None
        self.formated_sample = None

    def generate(self, indentifiers_for_everysample):
        if self.tagtog_sample is not None and self.formated_sample is not None:
            return self.tagtog_sample, self.formated_sample

        df = pd.read_csv(os.path.join(DATA_FOLDER, "serpFullArticlesScrape.csv"), delimiter = "\t")
        unique_df = remove_duplicates(df)
        keyword_counts = unique_df.apply(lambda x: keywordCount(x.headline if isinstance(x.headline, str) else "" + "\n" + x.content), axis = 1)

        selected = keyword_counts.apply(lambda cnts: False) 
        allChoices = []
        for kw in keywords.keys():
            matches = keyword_counts.apply(lambda cnts: cnts[kw]!= 0) & (~selected)
            choices = unique_df[matches].sample(min(30, sum(matches)), random_state=42)

            selected[choices.index] = True
            allChoices.append(choices)

        self.tagtog_sample = pd.concat(allChoices)
        self.formated_sample = self.tagtog_sample.apply(lambda x: "\n".join([str(x.name), x.title.replace("\n", ""), x.date.replace("\n", ""), str(x.headline).replace("\n", ""), x.content]), axis=1)

        indentifiers_for_everysample['keyword_stratified_1'] = set(self.tagtog_sample['link'])
        return self.tagtog_sample, self.formated_sample

    def formated_output_file(self):
        return os.path.join(FORMATED_SAMPLE_FOLDER, "6_22_2021_flood_keyword_full_articles.csv")
    
    def unformated_output_file(self):
        return os.path.join(UNFORMATED_SAMPLE_FOLDER, "Unformated_6_22_2021_flood_keyword_full_articles.csv")

class ExactMatchFloodDamage(Sample):
    def __init__(self) -> None:
        self.damaged_keywords = {
            "ক্ষয়ক্ষতি": "damage",
            "ক্ষয়": "damage",
            "ক্ষতিগ্রস্ত": "damaged",
            "নষ্ট": "damaged"
        }

        self.waterlogged_keywords = {
            "পানিবন্দী": "waterlogged",
            "নিমজ্জিত": "submerged",
            "পানিবন্দি": "waterlogged"
        }

        self.flood_keywords = {
            "বন্যা": "flood",
            "পাহাড়ি ঢলে": "steam coming down the hill",
            "বেড়িবাঁধ ক্ষতিগ্রস্ত": "embankment damaged",
            "বেড়িবাঁধ উপচে": "water overflew the embankment"
        }

        self.cyclone_keywords = {
            "ঘূর্ণিঝড়": "cyclone"
        }
        self.shammanul_keyword_pairs = set((fst, snd) for fst in self.flood_keywords.keys() for snd in self.damaged_keywords.keys() | self.waterlogged_keywords.keys())
        self.shammanul_keyword_pairs |= set((fst, snd) for fst in self.cyclone_keywords.keys() for snd in self.damaged_keywords.keys())

    def df_keyword_count(self, df, keywords, per_entry = False):
        if not isinstance(keywords, dict):
            keywords = {kw: None for kw in keywords}
            
        keyword_counts = df.apply(lambda x: keywordCount( (x.headline if isinstance(x.headline, str) else "") + "\n" + x.content, keywords), axis = 1)
        if per_entry:
            return keyword_counts
        counts = {keyword: len(df[keyword_counts.apply(lambda x: x[keyword] > 0)]) for keyword in keywords}
        counts['any'] = len(df[keyword_counts.apply(lambda x: any(x[keyword] > 0 for keyword in keywords))])
        return counts

    def stratified_sample(self, df, stratified_index, n_per_index = -1, random_state = 42):
        samples, cnts = [], {}
        for idx in list(stratified_index.sample())[0].keys():
            selection = df[stratified_index.apply(lambda idxs: idxs[idx])]
            if n_per_index < 0:
                samples.append(selection)
            else:
                samples.append(selection.sample(min(n_per_index, len(selection)), random_state = random_state))
            cnts[idx] = min(n_per_index, len(selection))
        return pd.concat(samples).drop_duplicates(['headline', 'content']), cnts

    def shammanul_filter(self, df, n_sample = None, random_state = 42):
        shammanul_keywords_single = self.damaged_keywords.keys() | self.waterlogged_keywords.keys() | self.flood_keywords.keys() | self.cyclone_keywords.keys()
        counts = self.df_keyword_count(df, {kw: "" for kw in shammanul_keywords_single}, per_entry=True)
        shammanul_pair_hits = counts.apply(lambda cnt: {(fst, snd):(cnt[fst]!=0 and cnt[snd]!=0) for fst, snd in self.shammanul_keyword_pairs})
        if n_sample is not None:
            return self.stratified_sample(df, shammanul_pair_hits, n_per_index=n_sample, random_state=random_state)
        return self.stratified_sample(df, shammanul_pair_hits)[0]

    def generate(self, indentifiers_for_everysample):
        if self.tagtog_sample is not None and self.formated_sample is not None:
            return self.tagtog_sample, self.formated_sample

        exact_match_serp_articles_raw = pd.read_csv("data_for_samples/serpExactMatchAllFullArticlesScrape.csv", delimiter = "\t")
        exact_match_serp_articles = remove_duplicates(exact_match_serp_articles_raw)
        exact_match_sample = self.shammanul_filter(exact_match_serp_articles, n_sample=10) 

        self.tagtog_sample = exact_match_sample[exact_match_sample['link'].apply(lambda link: all(link not in sample for sample in indentifiers_for_everysample.values()))]
        self.formated_sample = self.tagtog_sample.apply(lambda x: "\n".join([str(x.name), x.title.replace("\n", ""), x.date.replace("\n", ""), x.headline.replace("\n", ""), x.content]), axis=1)

        return self.tagtog_sample, self.formated_sample

    def formated_output_file(self):
        return os.path.join(FORMATED_SAMPLE_FOLDER, "7_5_2021_exact_match_articles.csv")
    
    def unformated_output_file(self):
        return os.path.join(UNFORMATED_SAMPLE_FOLDER, "Unformated_7_5_2021_exact_match_articles.csv")

def LargeBatch(Sample):
    pass

samples = {
    "bengali_articles_sample1": BengaliArticlesSample1(),
    "begali_articles_has_keyword_samples": BengaliFloodKeywords(),
    #"prothom_alo_flood": ProthomAlo(),
    "keyword_stratified": KeywordStratified(),
    "exact_match_with_shammanuls_filter": ExactMatchFloodDamage()
}

if __name__ == "__main__":
    indentifiers_for_everysample = {}
    for sample_name, sample in samples.items():
        sample.generate(indentifiers_for_everysample)
        try:
            sample.save()
        except AssertionError as e:
            print(f"{sample_name} does not match recorded sample")
            raise e
