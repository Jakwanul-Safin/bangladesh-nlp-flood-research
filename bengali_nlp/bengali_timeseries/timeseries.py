import os
import pandas as pd
import pickle

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta

def gaussian_kernel(sigma = 15, window = None):
    """Returns a Gaussian Kernel with mean 0 and a given window size"""
    if window == None:
        window = 6 * sigma + 1
    else:
        assert(window % 2 == 1)
    
    X = np.arange(-window//2, window//2 + 1)
    y = (1/(np.pi*sigma))**(1/2) * np.exp(-X**2/sigma**2)
    y /= np.linalg.norm(y)
    return y

class TimeSeries:
    def __init__(self, X, y):
        self.X = X
        self.y = y
    
    def from_dates(dates,
                weights = None,
                date_range = (datetime(2010, 1, 1), datetime.now()), 
                resolution = timedelta(days = 1),
                pad = 15,
                ):
        """Converts a set of dates into a histogram"""
        days_from_now = np.array([(datetime.now() - x).days for x in dates])
        y, days_bins = np.histogram(dates, bins = np.arange(date_range[0], date_range[1] + pad * resolution, resolution),
                                    weights = weights
                                   )
        X = days_bins[:-1]
        return TimeSeries(X, y)
    
    def plot(self, label = None):
        if label is not None:
            plt.plot(self.X, self.y, label = mn)
        else:
            plt.plot(self.X, self.y)
    
    def full_plot(self, 
             title = None, 
             xlabel = 'Date', 
             ylabel = "Frequency"
            ):  
        fig=plt.figure(figsize=(15,7), dpi= 100, edgecolor='k')

        self.plot(smooth)
        if title is not None:
            plt.title(title)
        if xlabel is not None:
            plt.xlabel(xlabel)
        
        if ylabel is not None:
            plt.ylabel(ylabel)
        plt.show()
    
    def smoothed(self, sigma = 15):
        y_smoothed = np.convolve(self.y, gaussian_kernel(sigma=sigma), "same")
        return TimeSeries(self.X, y_smoothed)
    
    def save(self, fn, overwrite = False):
        if not overwrite:
            if os.path.exists(fn):
                raise FileExistsError("Save file already exists. Set overwrite to True to overwrite file.")

        with open(fn, 'wb') as f:
            pickle.dump((self.X, self.y), f)
    
    def load(fn, smooth = None):
        with open(fn, 'rb') as f:
            X, y = pickle.load(f)
        return TimeSeries(X, y)