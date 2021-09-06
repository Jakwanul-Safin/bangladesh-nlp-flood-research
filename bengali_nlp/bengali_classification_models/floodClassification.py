from abc import ABC, abstractclassmethod, abstractmethod

class FloodClassificationModel(ABC):

    @abstractclassmethod
    def predict(batch):
        raise NotImplementedError

    @abstractmethod
    def load_pretrained(fold):
        raise NotImplementedError