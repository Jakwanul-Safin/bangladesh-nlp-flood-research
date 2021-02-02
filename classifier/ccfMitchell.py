#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:37:58 2020

@author: Mitchell
"""
import scipy.signal as signal
from scipy.stats import spearmanr
from scipy.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt
import math


# R ccf function converted to python
# x and y are two arrays of equal length
# lag_max is the maximum lag in the ccf function
# conf_interval allows a custom confidence interval to be passed
def ccf(x, y, tupList=False, ccf_type="CCF", lag_max=20, conf_interval=None,
        plot=False, title='', subtitle=None, rOutput=False, plt_args={}):
    xticksFontSize=plt_args.get('xticksFontSize',16)
    yticksFontSize=plt_args.get('yticksFontSize',16)
    xlabelFontSize=plt_args.get('xlabelFontSize',16)
    ylabelFontSize=plt_args.get('ylabelFontSize',16)
    titleFontSize=plt_args.get('titleFontSize',16)
    legendFontSize=plt_args.get('legendFontSize',16)
    figSize=plt_args.get('figSize',(10,5))
    
    if tupList:
        assert len(x) == len(y) and np.prod([x[i][0] == y[i][0] for i in range(len(x))]) == 1
        x = [i[1] for i in x]
        y = [i[1] for i in y]
    result, pval = spearmanr(x,y)
    result2, pval2 = pearsonr(x,y)
    print('Spearmen Corr, pval: {}, p-val={}, n={}'.format(round(result,4), pval, len(x)))
    print('Pearson Corr, pval: {}, p-val={}, n={}'.format(round(result2,4), pval2, len(x)))
    return (round(result,4), pval, len(x)), (round(result2,4), pval2, len(x))
#     result = signal.correlate(x - np.mean(x), y - np.mean(y), method='direct') / (np.std(x) * np.std(y) * len(x))
#     length = (len(result) - 1) // 2
#     lo = length - lag_max
#     hi = length + (lag_max + 1)

#     #    f, ax = plt.subplots(figsize = (10,5))
#     #    ax.stem(np.arange(-lag_max,lag_max+1), signal.correlate(x,y)[lo:hi], '-.')

#     if plot:
#         f, ax = plt.subplots(figsize=figSize)
#         maxX, maxY = np.argmax(result[lo:hi]), np.max(result[lo:hi])
#         xMap = {v: k for k, v in zip(np.arange(-lag_max, lag_max + 1), range(len(result[lo:hi])))}
#         ax.stem(np.arange(-lag_max, lag_max + 1), result[lo:hi], '-.')
#         ax.set_xticks(np.arange(-lag_max, lag_max + 1), lag_max / 5)
#         ax.set_xlabel("Lag", fontsize=xlabelFontSize)
#         ax.set_ylabel(ccf_type, fontsize=ylabelFontSize)
#         ax.annotate(str(round(maxY, 4)), (xMap[maxX], maxY))
#         if title:
#             f.suptitle(title, fontsize=titleFontSize)
#         if subtitle:
#             ax.set_title(subtitle)
#         if conf_interval:
#             conf95 = conf_interval
#         else:
#             conf95 = 1.96 / math.sqrt(len(x))
#         ax.axhline(conf95)

#         plt.show()

#     if rOutput: return result[lo:hi]