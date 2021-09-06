from bengali_classification_models.floodClassification import FloodClassificationModel
import pandas as pd

class KeywordModel(FloodClassificationModel):
    damaged_keywords = {
        "ক্ষয়ক্ষতি": "damage",
        "ক্ষয়": "damage",
        "ক্ষতিগ্রস্ত": "damaged",
        "নষ্ট": "damaged"
    }
    
    waterlogged_keywords = {
        "পানিবন্দী": "waterlogged",
        "নিমজ্জিত": "submerged",
        "পানিবন্দি": "waterlogged"
    }
    
    flood_keywords = {
        "বন্যা": "flood",
        "পাহাড়ি ঢলে": "steam coming down the hill",
        "বেড়িবাঁধ ক্ষতিগ্রস্ত": "embankment damaged",
        "বেড়িবাঁধ উপচে": "water overflew the embankment"
    }
    
    cyclone_keywords = {
        "ঘূর্ণিঝড়": "cyclone"
    }
    
    def predict(self, batch):
        shammanul_keywords_single = KeywordModel.damaged_keywords.keys() | KeywordModel.waterlogged_keywords.keys() | KeywordModel.flood_keywords.keys() | KeywordModel.cyclone_keywords.keys()
        counts = pd.DataFrame([{kw: txt.count(kw) for kw in shammanul_keywords_single} for txt in batch])
        dmged = counts[list(KeywordModel.damaged_keywords.keys() | KeywordModel.waterlogged_keywords.keys())].sum(axis=1)
        flooded = counts[list(KeywordModel.flood_keywords.keys() | KeywordModel.cyclone_keywords.keys())].sum(axis=1)
        return (dmged > 0) & (flooded > 0)

    def load_pretrained(fold):
        return KeywordModel()