import torch
from torch.utils.data import DataLoader, Dataset

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

class BagOfWords(Dataset):
  def __init__(self, text, labels, vect = TfidfVectorizer(), train = False):
    self.vect = vect
    if train:
      self.vectorized = vect.fit_transform(text)
    else:
      self.vectorized = vect.transform(text)
    self.labels = [int(i) for i in labels]

  def __len__(self):
    return self.vectorized.shape[0]

  def __getitem__(self, i):
    return torch.tensor(self.vectorized[i].todense(), dtype=torch.float32), self.labels[i]

  def vocab_size(self):
    return self.vectorized.shape[1]
  
  def vectorizer(self):
    return self.vect