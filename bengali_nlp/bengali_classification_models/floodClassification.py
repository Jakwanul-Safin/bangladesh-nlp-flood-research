from abc import ABC, abstractclassmethod, abstractmethod

class FloodClassificationModel(ABC):

    @abstractclassmethod
    def predict(self, batch):
        raise NotImplementedError()

    @abstractclassmethod
    def load_pretrained(cls, fold):
        raise NotImplementedError()

    @abstractmethod
    def train(self, train_data):
        raise NotImplementedError()

    @abstractmethod
    def test(self, test_data):
        raise NotImplementedError()