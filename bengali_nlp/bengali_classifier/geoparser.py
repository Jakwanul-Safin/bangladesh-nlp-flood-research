from abc import ABC, abstractclassmethod
from collections import defaultdict
from ..bengali_tools.locations import get_locations
from ..bengali_tools.bengali_preprocessing import preprocess_bangla

class BengaliGeoParser(ABC):
    def __init__(self, locations = None):
        if locations is None:
            locations = get_locations()

        self.upazilas = locations['upazilas']
        self.districts = locations['districts']
        self.divisions = locations['divisions'] 

    @abstractclassmethod
    def locate(self, text):
        raise NotImplementedError()

    @abstractclassmethod
    def locations(self):
        raise NotImplementedError

class OccurrenceGeoParser(BengaliGeoParser):
    def locate(self, text, level = 0, thres = 30, USE_MAX_OCCURING = False, AS_TOKENS = False):
        if not AS_TOKENS:
            tokens = preprocess_bangla(text)
    
        div, dis, upa = self.votes(tokens)
        if level == 0:
            n = sum(div.values())

        if USE_MAX_OCCURING:
            return max(div.keys(), key = lambda k: div[k])

        return tuple(k for k in div.keys() if div[k]/n *100 > thres)
    
    def locations(self, level = 0):
        return set(self.divisions.values())

    def votes(self, tokens):
        division_flooding = defaultdict(int)
        district_flooding = defaultdict(int)
        upazila_flooding = defaultdict(int)

        for tk in tokens:
            if tk in self.districts:
                division_flooding[self.districts[tk].split(".")[0]] += 1
                district_flooding[self.districts[tk]] += 1
                
                for k, upazila in self.upazilas.items():
                    district = ".".join(upazila.split(".")[:2])
                    if district == self.districts[tk]:
                        upazila_flooding[upazila] += 1

            elif tk in self.upazilas:
                division_flooding[self.upazilas[tk].split(".")[0]] += 1
                district_flooding[".".join(self.upazilas[tk].split(".")[:2])] += 1
                upazila_flooding[self.upazilas[tk]] += 1

        return division_flooding, district_flooding, upazila_flooding
