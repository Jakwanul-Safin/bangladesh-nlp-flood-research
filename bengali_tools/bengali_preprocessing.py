import sys
sys.path.append("..")
from basic_bengali_tools import *

from bnlp import BasicTokenizer
from bnlp.corpus import stopwords

tokenizer = BasicTokenizer()

class BengaliStandardizer:
    def standandize(self, text):
        text = text.replace('ড়', 'ড'+ '়')
        text = text.replace('র', 'ব' + '়')
        text = text.replace('ঢ়', 'ঢ'+'়')
        text = text.replace('য়', 'য'+ '়')
        return text

class BengaliStemmer:
    def stem_token(self, word):
        if word[-2:] == 'সহ':
            return (word[:-2], 'সহ')
        return (word, )
    
    def stem(self, tokens):
        return (stk for tk in tokens for stk in self.stem_token(tk))

class BengaliTokenizer:
    def __init__(self, stopwords=stopwords, num_token = True):
        self.tokenizer = BasicTokenizer()
        self.stopwords = stopwords
        self.num_token = num_token
    
    def tokenize(self, text):
        tokens = [tk for tk in tokenizer.tokenize(text) if tk not in stopwords and all(c in bengaliTextChars for c in tk)]
        if self.num_token == True:
            for i, tk in enumerate(tokens):
                if len(tk) > 1 and all(c in digits for c in tk):
                    tokens[i] = '<NUM>'
        return tokens

def preprocess_bangla(text,  tokenizer = BengaliTokenizer(), 
                      stemmer = BengaliStemmer(), 
                      standardizer = BengaliStandardizer(),
                      as_tokens = True
                      ):
    
    text = standardizer.standandize(text)
    tokens = tokenizer.tokenize(text)
    stemmed_tokens = stemmer.stem(tokens)
    
    if as_tokens:
        return list(stemmed_tokens)
    else:
        return " ".join(stemmed_tokens)