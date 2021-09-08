from abc import ABC, abstractclassmethod

import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Event:
    dates: Tuple[datetime, datetime]
    locs: List[str]
        
    def __repr__(self):
        locs_str = ",".join(loc.capitalize() for loc in self.locs)
        start_date_str = self.dates[0].strftime("%B %d, %Y")
        end_date_str = self.dates[1].strftime("%B %d, %Y")
        return f"Flood event from {start_date_str} to {end_date_str} in {locs_str}"

class EventDetector(ABC):
    
    @abstractclassmethod
    def events(self):
        raise NotImplementedError()

class SateliteTSEventDetector(EventDetector):
    def __init__(self, timeseries, location, height_thres_mean_frac = 0.25, height_thres_ignore_bellow = 0.1):
        self.timeseries = timeseries
        self.height_thres_mean_frac = height_thres_mean_frac
        self.height_thres_ignore_bellow = height_thres_ignore_bellow
        self.location = location
    
    def events(self, smoothing = 15):
        height_thres = self.height_thres_mean_frac * np.mean(self.timeseries.y[self.timeseries.y > self.height_thres_ignore_bellow])
        self.events, _ = find_peaks(self.timeseries.smoothed(smoothing).y, height = height_thres, width = smoothing)
        return [Event(dates=(date, date), locs = [self.location]) for date in self.timeseries.X[self.events]]
    
    def plot(self, smoothing = 15, label_date = True):
        X = self.timeseries.X[self.events]
        y = self.timeseries.smoothed(smoothing).y[self.events]
        plt.scatter(X, y, color='r')
        
        if label_date:
            for a, b in zip(X, y):
                plt.annotate(a.strftime("%b/%d/%y"), (a, b))

class NewsMediaEventDector(EventDetector):
    def __init__(self, timeseries, articles, geolocator): 
        pass
    
    def events(self):
        # Events are peaks which occur in the same general division. They may span multiple regions however
        return