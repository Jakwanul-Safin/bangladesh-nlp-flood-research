import os
from bengali_article_classification.load_classification_data import getFivefoldWithUnlabelled, getEnglishDataset

import torch
from simpletransformers.classification import ClassificationModel, ClassificationArgs
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

import numpy as np, pandas as pd

from bengali_classification_models.banglaBERT import BanglaBERT

ROOT = ""
NLP_ROOT = ""
dataset_root = os.path.join(NLP_ROOT, "bengali_article_classification")
df, df_id, X_trains, X_tests, y_trains, y_tests, X_u = getFivefoldWithUnlabelled(ROOT=dataset_root)
eng_df, eng_df_id, eng_X_train, eng_X_test, eng_y_train, eng_y_test = getEnglishDataset(ROOT=dataset_root)

def getMultiLingualBERT( 
    model_args =  ClassificationArgs(
        num_train_epochs=5,
        max_seq_length=512,
        no_save = True,
        overwrite_output_dir=True
    )
  ):
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  assert(torch.cuda.is_available())

  return ClassificationModel(
      "bert", "bert-base-multilingual-uncased", 
      args=model_args,
      use_cuda=torch.cuda.is_available()
  )

english_training_df = eng_df.rename({"is_flood": "label"}, axis=1)
bengali_training_df = pd.concat([pd.Series.to_frame(X_trains[0]), pd.Series.to_frame(y_trains[0], name="label")], axis = 1)
bengali_test_df = pd.concat([pd.Series.to_frame(X_tests[0]), pd.Series.to_frame(y_tests[0], name="label")], axis = 1)

ENGLISH_ONLY, ENGLISH_BENGALI_LABELLED, ENGLISH_BENGALI_ALL = range(3)
exp_tags = {
    ENGLISH_ONLY: "EngOnly",
    ENGLISH_BENGALI_LABELLED: "Eng+BengLabelled",
    ENGLISH_BENGALI_ALL: "Eng+BengAll"
}

exp_tag = exp_tags[ENGLISH_BENGALI_ALL]

CLTS_df = pd.read_csv(os.path.join(NLP_ROOT, "bengali_crosslingual", "CLTS_predictions.csv"), index_col=0)\
  .rename({"student_pred_id": "label"}, axis = 1)[["text", "label"]]

def get_dataset(bangla_labelled = False, bangla_unlabelled = False, english = False):
    datasets = [bengali_training_df, CLTS_df, english_training_df]
    to_use = [bangla_labelled, bangla_unlabelled, english]
    return pd.concat([ds for ds, use in zip(datasets, to_use) if use]),\
         "_".join(l for l, use in zip(['labBe', 'unlabBe', 'eng'], to_use) if use)

def eng_bengali_multilingual_bert_fold():
    model = getMultiLingualBERT()

    eng_beng_training_df = pd.concat([english_training_df, bengali_training_df, CLTS_df])
    model.train_model(eng_beng_training_df)

    save_file = os.path.join(ROOT, f"eng-bengali-multilingual_bert_fold_{exp_tag}.ckpt")
    torch.save(model.model.state_dict(), save_file)

    true = bengali_test_df['label']
    preds, model_outputs = model.predict(list(bengali_test_df['text']))

    print("Classification Report")
    print(classification_report(true, preds))

    print("Confusion Matrix")
    print(confusion_matrix(true, preds))

    acc = accuracy_score(true, preds)
    pre, rec, fsc, _ = precision_recall_fscore_support(true, preds, average = "binary")

    print(f"Accuracy: {acc}\nPrecision: {pre}\nRecall:{rec}\nF-score:{fsc}")

MULTILINGUAL_BERT, BANGLA_BERT = "multilingual_bert", "bangla_bert"
def get_model(option = MULTILINGUAL_BERT):
    if option == MULTILINGUAL_BERT:
        return getMultiLingualBERT(), MULTILINGUAL_BERT
    elif option == BANGLA_BERT:
        return BanglaBERT(), BANGLA_BERT


def run_train(model_type, bangla_labelled = False, bangla_unlabelled = False, english = False):
    model, m_name = get_model(model_type)
    dataset, ds_name = get_dataset(
        bangla_labelled = bangla_labelled, 
        bangla_unlabelled = bangla_unlabelled, 
        english = english)
    
    model.train_model(dataset)

    save_file = os.path.join(ROOT, f"{ds_name}-{m_name}.ckpt")
    torch.save(model.model.state_dict(), save_file)

    true = bengali_test_df['label']
    preds, model_outputs = model.predict(list(bengali_test_df['text']))

    print("Classification Report")
    print(classification_report(true, preds))

    print("Confusion Matrix")
    print(confusion_matrix(true, preds))

    acc = accuracy_score(true, preds)
    pre, rec, fsc, _ = precision_recall_fscore_support(true, preds, average = "binary")

    print(f"Accuracy: {acc}\nPrecision: {pre}\nRecall:{rec}\nF-score:{fsc}")