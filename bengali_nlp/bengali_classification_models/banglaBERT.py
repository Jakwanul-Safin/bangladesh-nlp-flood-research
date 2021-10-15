from bengali_classification_models.floodClassification import FloodClassificationModel
from transformers import BertTokenizer, BertForMaskedLM

import os
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn

from tqdm.auto import tqdm

def full_report(true, preds):
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

    print("Classification Report")
    print(classification_report(true, preds))

    print("Confusion Matrix")
    print(confusion_matrix(true, preds))

    acc = accuracy_score(true, preds)
    pre, rec, fsc, _ = precision_recall_fscore_support(true, preds, average = "binary")

    print(f"Accuracy: {acc}\nPrecision: {pre}\nRecall:{rec}\nF-score:{fsc}")

class BengaliNewsDataset(Dataset):
    def __init__(self, X, y = None):
        if y is None:
            self.X, self.y = X['content'], X['is_flood']
        else:
            self.X, self.y = X, y
    
    def __getitem__(self, i):
        return self.X.iloc[i], self.y.iloc[i]
    
    def __len__(self):
        return len(self.y)

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
    def __init__(self, model = None):
        if model == None:
            self.model = Bangla_Based_BERT_Classifier(BertForMaskedLM.from_pretrained("sagorsarker/bangla-bert-base"))
        else:
            self.model = model
        self.tokenizer = BertTokenizer.from_pretrained("sagorsarker/bangla-bert-base")

    def collate_batch(self, batch, MAX_SEQ_LEN = 512):
        text = batch
        text_enc = self.tokenizer(text, padding="max_length", truncation=True, return_tensors = "pt", max_length=MAX_SEQ_LEN)
        
        return text_enc.to(self.device)

    def train_model(self, train_ds, batch_size = 8, use_cuda = torch.cuda.is_available()):
        from transformers import get_scheduler, AdamW

        device = torch.device("cuda" if use_cuda else "cpu")
        ds = DataLoader(BengaliNewsDataset(train_ds['text'], train_ds['label']), batch_size = batch_size, shuffle=False, collate_fn = self.collate_batch)

        optimizer = AdamW(self.model.parameters())

        num_epochs = 40
        save_every = 8
        num_training_steps = num_epochs * len(ds)
        lr_scheduler = get_scheduler(
            "linear",
            optimizer=optimizer,
            num_warmup_steps=0,
            num_training_steps=num_training_steps
        )

        progress_bar = tqdm(range(num_training_steps))
        criterion = nn.BCEWithLogitsLoss()

        #trainables = ['cls', 'classifier']
        #for name, p in bangla_based_bert.named_parameters():
        #if any(tname in name for tname in trainables):
        #    p.requires_grad = True
        #else:
        #    p.requires_grad = False

        loss_hist, accuracy_hist = [], []
        for epoch in range(num_epochs):
        
            with tqdm(ds, unit = "batch") as tepoch:
                n, accuracy = 0, 0
                t_pred, f_pred = 0, 0 

                for data, target in tepoch:
                    data, target = data.to(device), target.to(device)

                    optimizer.zero_grad()
                    logits_pred = self.model(data)
                    loss = criterion(logits_pred, target.unsqueeze(1))
                    loss.backward()
                    optimizer.step()
                        
                    lr_scheduler.step()
                    progress_bar.update(1)
                    tepoch.set_postfix(loss = loss.item())
                    loss_hist.append(loss.item())
                
            #if (epoch + 1) % save_every == 0:
            #    torch.save(bangla_based_bert, os.path.join(ROOT, f"{training_set_flag}bangla_bert_epoch_{epoch+1}_fold_{FOLD_INDEX}.ckpt"))
                
            if (epoch + 1) % (save_every//2) == 0:
                #target, pred = test_bangla_based_bert()

                print(f"Epoch:{epoch+1}")
                #full_report(target, pred)

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
        return preds, output

    def load_pretrained(fold, epoch = 32, root='', use_cuda = torch.cuda.is_available()):
        device = torch.device("cuda" if use_cuda else "cpu")
        model = torch.load(os.path.join(root, "models/BanglaBERT", f"bangla_bert_epoch_{epoch}_fold_{fold}.ckpt"), map_location = device)
        return BanglaBERT(model)