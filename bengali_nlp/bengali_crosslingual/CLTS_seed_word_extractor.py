from abc import ABC, abstractmethod
from time import time
import os

import json

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import l1_min_c

class Translator(ABC):
    @abstractmethod
    def translate_seedword(self, word):
        raise NotImplementedError()

class GoogleTranslator(Translator):
    def __init__(self, translator = None, saved_translations_file = "en_bd_dict.json", ROOT = ''):
        self.translator = translator
        self.saved_translations_file = os.path.join(ROOT, saved_translations_file)
        if os.path.exists(self.saved_translations_file):
          with open(self.saved_translations_file, 'r') as f:
              self._dict = json.load(f)
        else:
          self._dict = {}
          print("Could not find translation file")

    def translate_seedword(self, word):
        if word in self._dict:
            return self._dict[word]
        translate = self.translator.translate(word, 'bn', 'en')["text"]
        self._dict[word] = translate
        return translate

    def get_translation_dict(self, source_words):
      translation_dict = {}
      for source_word in source_words:
        target_word = self.translate_seedword(source_word)
        if target_word == "":
          continue
        if len(target_word.split(" ")) > 1:
          continue
        translation_dict[source_word] = target_word
      return translation_dict

    def transfer_weights(self, source_words):
      translation_dict = self.get_translation_dict(list(source_words.keys()))
      target_words = {translation_dict[word]:weight for word, weight in source_words.items() if word in translation_dict}
      return target_words

    def save(self):
        with open(self.saved_translations_file, 'w') as f:
            json.dump(self._dict, f)

class SeedwordExtractor:
    def __init__(self, source_language, target_language, num_seeds, label2ind):
        self.source_language = source_language
        self.target_language = target_language
        self.num_seeds = num_seeds  # refers to source language
        self.label2ind = label2ind
        self.ind2label = {label2ind[a]: a for a in label2ind}

    def extract_seedwords(self, features, labels, vocabulary, 
                    classification_type = 'binary',
                    random_state=1000):

        clf = LogisticRegression(penalty='l1', random_state=random_state, tol=1e-6, max_iter=int(1e6), solver='liblinear', multi_class='ovr')
        # Regularization path: tune C so that we get the #coefficients we ask for.
        best_c = tune_C_regularization_path(clf, features, labels, ind2label=self.ind2label, num_steps=50, num_seeds=self.num_seeds)
        print("best C: {}".format(best_c))
        clf.set_params(C=best_c)

        print("SOURCE CLF: #features={}".format(features.shape[1]*len(set(labels))))
        clf.fit(features, labels)

        word2ind = vocabulary
        ind2word = {i: w for w, i in word2ind.items()}

        # Get scores provided by LogReg
        if len(clf.classes_) == 2 and classification_type == 'binary':
            # binary classification: classifier is a single vector
            aspect2indices = {
                1: np.argsort(clf.coef_[0])[::-1], # pos class (rank highest->lowest)
                0: np.argsort(clf.coef_[0])        # neg class (rank lowest->highest)
            }
            aspect_score_dict = {
                self.ind2label[0]: [(ind2word[sw_ind], clf.coef_[0][sw_ind]) for sw_ind in aspect2indices[0] if clf.coef_[0][sw_ind] < 0],
                self.ind2label[1]: [(ind2word[sw_ind], clf.coef_[0][sw_ind]) for sw_ind in aspect2indices[1] if clf.coef_[0][sw_ind] > 0]}
            weight_dict = {ind2word[i]: clf.coef_[:, i] for aspect in aspect2indices for i in aspect2indices[aspect][:self.num_seeds]}
        else:
            aspect2indices = {i: np.argsort(clf.coef_[i])[::-1] for i in clf.classes_}
            aspect_score_dict = {self.ind2label[i]: [(ind2word[sw_ind], clf.coef_[i][sw_ind]) for sw_ind in aspect2indices[i] if clf.coef_[i][sw_ind]>0] for i in clf.classes_}
            # Get weights for the top <num_seeds> words per aspect.
            weight_dict = {ind2word[i]: clf.coef_[:, i] for aspect in aspect2indices for i in aspect2indices[aspect][:self.num_seeds]}
        self.clf = clf
        self.source_seedword_weights = weight_dict
        self.all_source_word_weights = aspect_score_dict
        return weight_dict, clf

def tune_C_regularization_path(clf, features, labels, ind2label, num_steps=16, num_seeds=50):
    # select the top <num_seeds> seed words for each aspect
    clf.set_params(warm_start=True)
    min_c = 1  # 10^0
    max_c = 8  # 10^7
    # Regularization path
    # Return the lowest bound for C such that for C in (l1_min_C, infinity) the model is guaranteed not to be empty.
    # cs: a list of possible c values to try
    cs = l1_min_c(features, labels, loss='log') * np.logspace(min_c, max_c, num_steps)
    print("Computing regularization path ...")
    start = time()
    coefs_ = []
    for c in cs:
        clf.set_params(C=c)
        clf.fit(features, labels)
        coefs_.append(clf.coef_.copy())
        pos = np.sum(clf.coef_ > 0, axis=1)
        if len(ind2label) == 2:
            # binary classification; do same as other
            pos = np.sum(clf.coef_ > 0, axis=1)
            neg = np.sum(clf.coef_ < 0, axis=1)

            flags = [pos[0] > num_seeds, neg[0] > num_seeds]
        else:
            # multiclass classification
            flags = [pos[i] > num_seeds for i in ind2label]
        if not False in flags:
            print("This took %0.3fs" % (time() - start))
            return c
    print("This took %0.3fs" % (time() - start))
    return c