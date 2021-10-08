import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import joblib
import os
import re


identity_fn = lambda v: v

def split_to_sentences(text):
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)

class StudentBERT:
    def __init__(self, clf, manual_seed=1993):
        print("Compiling BERT Student")
        self.clf = clf
        self.manual_seed = manual_seed

    def train(self, df, eval_df=None, label_name='label', eval_label_name='label'):
      train_df = self.postprocess_df(df, label_name=label_name)
      if eval:
          eval_df = self.postprocess_df(eval_df, label_name=eval_label_name)

      self.clf.train_model(train_df, eval_df=eval_df)

    def eval(self, df, label_name='label'):
        test_df = self.postprocess_df(df, label_name=label_name)
        result, model_outputs, wrong_predictions = self.clf.eval_model(test_df, acc=sklearn.metrics.accuracy_score)
        pred = np.argmax(model_outputs, axis=1)
        print(f"Accuracy: {result}")
        return pred

    def postprocess_df(self, df, label_name='label'):
        text = df['text'].map(lambda x: " ".join(split_to_sentences(x)[:10])).tolist()
        labels = df[label_name].map(lambda x: self.label2ind[x]).tolist()
        return pd.DataFrame(list(zip(text, labels)))

class Student:
    def __init__(self, label2ind, tokenizer=None, manual_seed=1993):
        print("Compiling Student")
        self.num_labels = len(label2ind)
        self.label2ind = label2ind
        self.manual_seed = manual_seed

        self.tokenizer = tokenizer
        if not self.tokenizer:
            raise(Exception("Need to define tokenizer for student={}".format(self.name)))
        self.vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.9, norm='l2', ngram_range=(1, 2),
                                          analyzer='word', tokenizer=identity_fn, preprocessor=identity_fn, token_pattern=None)
        self.clf = LogisticRegression(random_state=self.manual_seed, max_iter=int(1e6))

    def train(self, df, label_name='label'):
        tokenized_text = df['text'].map(lambda x: self.tokenizer(x))
        features = self.vectorizer.fit_transform(tokenized_text).toarray()
        labels = df[label_name].map(lambda x: self.label2ind[x])
        self.clf.fit(features, labels)
        print("logreg features: {}".format(self.clf.coef_.shape[1] * self.clf.coef_.shape[0]))

    def eval(self, df, label_name='label'):
        tokenized_text = df['text'].map(lambda x: self.tokenizer(x))
        features = self.vectorizer.transform(tokenized_text).toarray()
        print("logreg features: {}".format(features.shape))
        pred = self.clf.predict(features)
        return pred

    def save(self, savefolder):
        joblib.dump(self.clf, os.path.join(savefolder, 'student_clf.pkl'))
        if self.name == 'logreg':
            joblib.dump(self.vectorizer, os.path.join(savefolder, 'student_vectorizer.pkl'))