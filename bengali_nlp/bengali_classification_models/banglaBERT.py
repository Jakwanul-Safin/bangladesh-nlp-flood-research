from bengali_classification_models.floodClassification import FloodClassificationModel
from transformers import BertTokenizer, BertModel

import os
import torch
from torch.utils.data import DataLoader
import torch.nn as nn

from tqdm.auto import tqdm

class Bangla_Based_BERT_Classifier(nn.Module):
    def __init__(self, bert_model):
        super(Bangla_Based_BERT_Classifier, self).__init__()
        
        self.bert = bert_model

        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(102025, 1)
        )
        
    def forward(self, X):
        output = self.bert(**X)
        class_out = output['logits'][:, 0, :]
        logits = self.classifier(class_out)
        return logits
    
    def train(self):
        self.bert.train()

class BanglaBERT(FloodClassificationModel):
    def __init__(self, model):
        self.model = model
        self.tokenizer = BertTokenizer.from_pretrained("sagorsarker/bangla-bert-base")

    def collate_batch(self, batch, MAX_SEQ_LEN = 512):
        text = batch
        text_enc = self.tokenizer(text, padding="max_length", truncation=True, return_tensors = "pt", max_length=MAX_SEQ_LEN)
        
        return text_enc.to(self.device)

    def predict(self, batch, use_cuda = torch.cuda.is_available()):
        
        self.device = torch.device("cuda" if use_cuda else "cpu")
        ds = DataLoader(list(batch), batch_size = 1, shuffle=False, collate_fn = self.collate_batch)
        progress_bar = tqdm(range(len(ds)))
        preds = []
        for X in ds:
          with torch.no_grad():
            output = self.model(X)
            pred = 1*(output > 0).squeeze()
            preds.append(pred.cpu().item())
          progress_bar.update(1)
        return preds

    def load_pretrained(fold, epoch = 32, root='', use_cuda = torch.cuda.is_available()):
        device = torch.device("cuda" if use_cuda else "cpu")
        model = torch.load(os.path.join(root, "models/BanglaBERT", f"bangla_bert_epoch_{epoch}_fold_{fold}.ckpt"), map_location = device)
        return BanglaBERT(model)