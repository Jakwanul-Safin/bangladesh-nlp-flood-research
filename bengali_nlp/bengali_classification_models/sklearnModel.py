from bengali_classification_models.floodClassification import FloodClassificationModel
import os, pickle

class SKlearnModel(FloodClassificationModel):
    def __init__(self, classifier, vectorizer):
        self.cls = classifier
        self.vect = vectorizer

    def predict(self, batch):
        X = self.vect.transform(batch)
        return self.cls.predict(X)

    def load_pretrained(fold, model_type = "LinearSVC", root = ""):
        if model_type in ['LinearSVC', 'LogRegL1', 'LogRegL2', 'RandomForest']:
            with open(os.path.join(root, "models", model_type, f"classifier_fold_{fold}"), 'rb') as f:
                cls = pickle.load(f)
            with open(os.path.join(root, "models", model_type, f"vectorizer_fold_{fold}"), 'rb') as f:
                vect = pickle.load(f)
            return SKlearnModel(cls, vect)
        raise NotImplementedError