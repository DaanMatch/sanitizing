#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv

import json

import pandas as pd

import numpy as np

import seaborn as sns
sns.set()

import random

import re

from my_nlp import *


# ## Read csv

# In[2]:


DarpanFcraDF = pd.read_csv('Darpan21FCRA.csv', dtype = {'S.No.': 'string', 'Registration': 'string'})


# ## Generate 10k random sample

# In[3]:


DarpanFcraDF = DarpanFcraDF.sample(n = 10000)
DarpanFcraDF.info()


# ## Write sample csv

# In[4]:


DarpanFcraDF.to_csv('SampleDarpan21FCRA.csv', index=False)


# # Make sets of IDs for all tags
# #### tags are "All", "FCRA", "URL", "MA1"

# In[5]:


TagsToIDVL = []
TagsToIDD = {}


# ### All NGO IDs

# In[6]:


AllIDV = set(DarpanFcraDF.UniqueID)


# In[7]:


TagsToIDVL.append({'tag': 'All', 'IDSet': AllIDV})
TagsToIDD['All'] = list(AllIDV)
len(AllIDV)


# ### FCRA number exists?

# In[8]:


FCRAV = set(DarpanFcraDF.UniqueID[DarpanFcraDF.FCRA.notnull()])


# In[9]:


TagsToIDVL.append({'tag': 'FCRA', 'IDSet': FCRAV})
TagsToIDD['FCRA'] = list(FCRAV)
len(FCRAV)


# ### URL exists?

# In[10]:


URLV = set(DarpanFcraDF.UniqueID[DarpanFcraDF['ngo url'].notnull()])


# In[11]:


TagsToIDVL.append({'tag': 'URL', 'IDSet': URLV})
TagsToIDD['URL'] = list(URLV)
len(URLV)


# ### Major activities exists?

# In[12]:


MA1V = set(DarpanFcraDF.UniqueID[DarpanFcraDF['Major Activities1'].notnull()])


# In[13]:


TagsToIDVL.append({'tag': 'MajorActivities', 'IDSet': MA1V})
TagsToIDD['MA1'] = list(MA1V)
len(MA1V)


# ## Write csv for tags and IDs
# https://www.geeksforgeeks.org/how-to-save-a-python-dictionary-to-a-csv-file/

# In[14]:


field_names = ['tag', 'IDSet']
with open('SampleTagsToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(TagsToIDVL)


# ## write json for tags and IDs
# https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/

# In[15]:


# TagsToIDD[tag] = [UniqueID]
with open("SampleTagsToIDList.json", "w") as outfile: 
    json.dump(TagsToIDD, outfile)


# # Make reverse look up dictionaries for Issues, States and Districts

# Issues:
# "Agriculture,Environment & Forests,Health & Family Welfare,"
# States:
# "UTTAR PRADESH, testingswss, UTTAR PRADESH, testingswss, UTTAR PRADESH,"
# Need to strip, remove '' and 'testingswss' and dedupe.

# In[16]:


IssueToIDD = {}
StateToIDD = {}
IDToStateDistD = {}
for index, row in DarpanFcraDF.iterrows():
    UniqueID = row['UniqueID']
    Issues = row['issues working db']
    States = row['operational states db']
    Dists =row['operational district db']

    # issues dict
    try:
        IssuesL = list(set(Issues.split(',')))
        IssuesL.remove('')
        for issue in IssuesL:
            if issue in IssueToIDD:
                IssueToIDD[issue].append(UniqueID)
            else:
                IssueToIDD[issue] = [UniqueID]
    except (AttributeError, ValueError):
        pass

    # states dict
    try:
        StatesL = list(set(map(lambda s: s.strip(), States.split(','))))
        StatesL.remove('')
        StatesL.remove('testingswss')
        for state in StatesL:
            if state in StateToIDD:
                StateToIDD[state].append(UniqueID)
            else:
                StateToIDD[state] = [UniqueID]
    except (AttributeError, ValueError):
        pass
    
    # districts list
    try:
        Dists1 = Dists.replace('->', ',')
        DistL = list(map(lambda s: s.strip(), Dists1.split(',')))
    except (AttributeError, ValueError):
        pass

    DistL = [elem for elem in DistL if elem != '']
    DistL = [elem for elem in DistL if elem != 'testingswss']
    
    # ID to states/districts
    IDToStateDistD[UniqueID] = {}
    for state in StatesL:
        IDToStateDistD[UniqueID][state] = []

    for location in DistL:
        if location in StatesL:
            state = location
        else:
            IDToStateDistD[UniqueID][state].append(location)

    for state in StatesL:
        IDToStateDistD[UniqueID][state] = list(set(IDToStateDistD[UniqueID][state]))
    


# In[17]:


StateDistToIDD = {}
for ID in IDToStateDistD:
    for state in IDToStateDistD[ID]:
        if state in StateDistToIDD:
            pass
        else:
            StateDistToIDD[state] = {}
        for dist in IDToStateDistD[ID][state]:
            if dist in StateDistToIDD[state]:
                StateDistToIDD[state][dist].append(ID)
            else: 
                StateDistToIDD[state][dist] = [ID]


# In[18]:


StatesL = list(StateDistToIDD.keys())
StatesSer = pd.Series(StatesL)

IssuesSer = pd.Series(list(IssueToIDD.keys()))


# ## write json for sets of NGOs in Issue, State and State, Dist
# https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/

# In[19]:


# IssueToIDD[issue] = [UniqueID]
with open("SampleIssueToIDList.json", "w") as outfile: 
    json.dump(IssueToIDD, outfile)

# StateToIDD[state] = [UniqueID]
with open("SampleStateToIDList.json", "w") as outfile: 
    json.dump(StateToIDD, outfile)

# StateDistToIDD[state][dist] = [UniqueID]
with open("SampleStateDistToIDList.json", "w") as outfile: 
    json.dump(StateDistToIDD, outfile)


# ## Write csv for sets of NGOs by feature

# ### Write csv for sets of NGOs by issue

# In[20]:


IssueToIDVL = []
for issue in IssueToIDD:
    IssueToIDVL.append({'issue': issue, 'IDSet': IssueToIDD[issue]})

field_names = ['issue', 'IDSet']
with open('SampleIssueToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(IssueToIDVL)


# ### Write csv for sets of NGOs by State

# In[21]:


StateToIDVL = []
for state in StateToIDD:
    StateToIDVL.append({'state': state, 'IDSet': StateToIDD[state]})

field_names = ['state', 'IDSet']
with open('SampleStateToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(StateToIDVL)


# ### Write csv for sets of NGOs by State and Dist

# In[22]:


StateDistToIDVL = []
for state in StateDistToIDD:
    for dist in StateDistToIDD[state]:
        StateDistToIDVL.append({'state': state, 'dist': dist, 'IDSet': StateDistToIDD[state][dist]})

field_names = ['state', 'dist', 'IDSet']
with open('SampleStateDistToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(StateDistToIDVL)


# # Filter NGOs

# ## Select Issues

# In[23]:


IssuesSer


# In[24]:


selection = input("Select index of (preferably) one issue (or indices of upto 3 Issues) you are interested in, separated by ',' ind1, ind2, ind3 from above list\n").split(',')

IDInIssuesV = set()
for ind in selection:
    print("Number of NGOs in Issue", IssuesSer[int(ind)], "=", len(IssueToIDD[IssuesSer[int(ind)]]))
    IDInIssuesV = IDInIssuesV.union(set(IssueToIDD[IssuesSer[int(ind)]]))
print("Number of NGOs in any of the Issues =", len(IDInIssuesV))


# ## Select Region (States or Districts in a State)

# In[26]:


DistrictsOrStates = str(input("To select up to 3 districts from a single state, type '1', else '0' - you will have the choice of selecting up to 3 states\n"))

if DistrictsOrStates == '1':
    print(StatesL,'\n')

    TheState = str(input("Select ONLY ONE state whose districts you are interested in\n"))

    StateDistL = list(StateDistToIDD[TheState].keys())
    print('\n', StateDistL, '\n')

    selection = str(input("Select upto 3 districts you are interested in from above list, separated by ','\n")).split(',')

    IDInRegionV = set()
    for dist in selection:
        print("number of NGOs in", dist, "=", len(StateDistToIDD[TheState][dist.strip()]))
        IDInRegionV = IDInRegionV.union(set(StateDistToIDD[TheState][dist.strip()]))
    print("number of NGOs in region = ", len(IDInRegionV))

else:
    print(StatesSer)
    selection = input("\nSelect indices of upto 3 states you are interested in, separated by ',' ind1, ind2, ind3 from above list\n").split(',')

    IDInRegionV = set()
    for ind in selection:
        print("number of NGOs in", StatesSer[int(ind)], "=", len(StateToIDD[StatesSer[int(ind)]]))
        IDInRegionV = IDInRegionV.union(set(StateToIDD[StatesSer[int(ind)]]))
    print("number of NGOs in region =", len(IDInRegionV))


# In[27]:


FinalV = IDInIssuesV.intersection(IDInRegionV)
print("Number of NGOs in Issues and region =", len(FinalV))


# ## Select tags

# In[28]:


FCRATag = str(input("Are you a looking to make a donation to an NGO in Foreign Currency?\n'1' for 'Yes' '0' for 'No'\n"))

FCRAReqV = AllIDV
if FCRATag == '1':
    FCRAReqV = FCRAV


# In[29]:


URLTag = str(input("Do you want to be able to explore the NGO's website?\n'1' for 'Yes' '0' for 'No'\n"))

URLReqV = AllIDV
if URLTag == '1':
    URLReqV = URLV


# In[30]:


MATag = str(input("Would you like to be able to see the NGO's description of Major Activities?\n'1' for 'Yes' '0' for 'No'\n"))

MAReqV = AllIDV
if MATag == '1':
    MAReqV = MA1V


# ## Final set

# In[31]:


FinalV = FinalV.intersection(FCRAReqV)
print("Number of filtered NGOs =", len(FinalV))


# In[32]:


FinalV = FinalV.intersection(URLReqV)
print("Number of filtered NGOs =", len(FinalV))


# In[33]:


FinalV = FinalV.intersection(MAReqV)
print("Number of filtered NGOs =", len(FinalV))


# In[ ]:





# # Show info for sample of 5

# In[34]:


FinalL = list(FinalV)
sampleL = random.sample(FinalL, 5)


# In[35]:


DarpanFcraDF.set_index("UniqueID", inplace=True)


# In[36]:


DarpanFcraDF.loc[sampleL][['Name', 'ngo url', 'Email', 'Mobile', 'Major Activities1', 'Secretary name', 'Secretary mobile', 'Secretary email']]


# In[ ]:




