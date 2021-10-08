import os
from bengali_article_classification.load_classification_data import getFivefoldWithUnlabelled, getEnglishDataset

import torch
from simpletransformers.classification import ClassificationModel, ClassificationArgs
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

import numpy as np, pandas as pd

NLP_ROOT = ".."
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