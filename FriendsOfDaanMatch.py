#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

from my_nlp import *

def name_cleaner(s, StopWords):
    s = depunctuate(s).lower()
    Tokens = tokenize(s)
    UnStopped = [t for t in Tokens if t not in StopWords]
    sL = list(set(UnStopped))
    sL.sort()
    CleanedName = ' '.join(sL)
    return CleanedName

Darpan21DF = pd.read_csv ('42621 Final_Data_ngodarpan.csv') #, low_memory = False)


Darpan21DF1 = Darpan21DF.dropna(subset = ['Name', 'fcrano'])


Darpan21DF1['CleanName'] = Darpan21DF1.apply(lambda row: name_cleaner(row.Name, SomeStopWordsV), axis = 1)



FcraDF = pd.read_csv ('FCRA - Sheet1.csv') #, low_memory = False)


FcraDF1 = FcraDF.dropna(subset = ['Registration', 'AssociationName'])


FcraDF1['CleanName'] = FcraDF1.apply(lambda row: name_cleaner(row.AssociationName, SomeStopWordsV), axis = 1)



DarpanFcraDF = Darpan21DF1.merge(FcraDF1, on = 'CleanName') #, how = 'right'


DarpanFcraDF.to_csv('42621_Final_Data_ngodarpan_V1.csv')
