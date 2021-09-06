from bengali_classification_models.floodClassification import FloodClassificationModel
from simpletransformers.classification import ClassificationModel, ClassificationArgs

import os
import torch

class EnglishTranslatedBERT(FloodClassificationModel):
    def __init__(self, model):
        self.model = model

    def predict(self, batch, lang = 'en'):
        # Translate batch
        if lang == 'en':
            return self.model.predict(list(batch))[0]
        else:
            raise NotImplementedError

    def load_pretrained(fold, root='', use_cuda = True):
        device = torch.device("cuda" if use_cuda else "cpu")

        model_args = ClassificationArgs(max_seq_length=512)
        model = ClassificationModel("bert", "bert-base-uncased", use_cuda = use_cuda)
        model.model.load_state_dict(torch.load(os.path.join(root, "models/EngTranslatedBERT", f"eng_translated_bert_fold_{fold}.ckpt"), map_location=device))

        return EnglishTranslatedBERT(model)