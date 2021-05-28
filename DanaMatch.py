#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv

import json

import pandas as pd

import numpy as np

import seaborn as sns
sns.set()

import re

from my_nlp import *


# In[65]:


import random


# # functions

# ## clean names of NGOs

# In[2]:


def name_cleaner(s, StopWords):
    s = depunctuate(s).lower()
    Tokens = tokenize(s)
    UnStopped = [t for t in Tokens if t not in StopWords]
    sL = list(set(UnStopped))
    sL.sort()
    CleanedName = ' '.join(sL)
    return CleanedName


# In[3]:


s = 'I am a rabbit! @ home with the bunnies? how are of the they/them cow and jump Over Moon. rabbit Rabbit they them are'
cleans = name_cleaner(s, SomeStopWordsV)
print(cleans)


# ## WIP pincode extract
# #### this is only the HQ pincode, not where they are active

# In[4]:


def extract_regex(regx, st):
    """ regx = raw string so no escape backslash"""
    pin_re = re.compile(regx) 
    m = pin_re.search(st)
    if m:
        pinS = m.group()
    else:
        pinS = ""
    return pinS


# In[5]:


#pincodes starting with '0' don't exist, those starting with '9' are APOs (Army Post Offices)
rgx = r"[1-8]\d{5}" # raw string so no escape backslash


# In[6]:


# no match
strng = r"https:// hey 103 feminisminindia.com/"
print(extract_regex(rgx, strng))


# In[7]:


# match
strng = r"some or the other address, bangloure, india, 567238, karnataka"
print(extract_regex(rgx, strng))


# In[8]:


# no '0' start pincodes
strng = r"#2 dhoop chhaon tree, bangloure, india, 067238, karnataka"
print(extract_regex(rgx, strng))


# In[9]:


# no '9' start pincodes which are Army POs
strng = r"some of the other address, bangloure, india, 967238, karnataka"
print(extract_regex(rgx, strng))


# In[10]:


# no less than 6 digits
strng = r"some of the other address, 534f67 bangloure, india, 67238, karnataka"
print(extract_regex(rgx, strng))


# In[11]:


# multiple pincodes extracts first valid only
strng = r"#2 dhoop chhaon tree,  bangloure 441007, india, 667238, karnataka"
print(extract_regex(rgx, strng))


# # Darpan21

# In[12]:


Darpan21DF = pd.read_csv('42621 Final_Data_ngodarpan.csv', dtype={"Mobile": 'string', "UniqueID": "string"                        , "fcrano": "string", "president mobile": "string", "Chairman mobile": "string", "Secretary mobile": "string"                        , "Asisstant Secretary mobile": "string", "Board Member mobile": "string", "Vice Chairman mobile": "string", "Member mobile": "string"                        , "issues working db": "string"}) #, low_memory = False)


# In[13]:


Darpan21DF.info()


# #### reg name has city name sometimes, do not use
# #### StateName clean and use with Name for matching

# In[14]:


Darpan21DF.drop(['reg name', 'status'], axis='columns', inplace=True)


# In[15]:


Darpan21DF.describe()


# ### histograms

# #### too long
# sns.countplot(Darpan21DF['Name'], color='gray')
# Darpan21DF.groupby('Name').size().plot(kind='bar')
# excel pivot table shows freq = 31 "CATHOLIC CHURCH", and a unique "catholic church" in addition to many other uniques with the name of the parish

# In[16]:


Darpan21DF['CleanName'] = Darpan21DF.apply(lambda row: name_cleaner(row.Name, SomeStopWordsV), axis = 1)
Darpan21DF['CleanState'] = Darpan21DF.apply(lambda row: name_cleaner(row.StateName, SomeStopWordsV), axis = 1)
Darpan21DF.info()


# # FCRA

# In[17]:


FcraDF = pd.read_csv('FCRA - Sheet1.csv', dtype = {'S.No.': 'string', 'Registration': 'string'}) #, low_memory = False)


# In[18]:


FcraDF.info()


# #### Note: "Nature" contains "Religious(Hindu) ,Cultural ,Educational ," etc info if we want to use it

# In[19]:


FcraDF.dropna(subset = ['Registration', 'AssociationName', 'Nature'], inplace = True)


# In[20]:


FcraDF.info()


# In[21]:


FcraDF.describe()


# #### FCRA DATA, address is too non-standard to parse easily, so just use "location" -which is state name- to match

# In[22]:


FcraDF['CleanName'] = FcraDF.apply(lambda row: name_cleaner(row.AssociationName, SomeStopWordsV), axis = 1)
FcraDF['CleanState'] = FcraDF.apply(lambda row: name_cleaner(row.Location, SomeStopWordsV), axis = 1)
FcraDF.info()


# # Merge the two datasets

# In[23]:


DarpanFcraDF = Darpan21DF.merge(FcraDF, on = ['CleanName', 'CleanState'], how = 'left') 


# In[24]:


DarpanFcraDF.info()


# In[25]:


DarpanFcraDF[['CleanName', 'CleanState', 'fcrano', 'Registration']].head()


# In[26]:


DarpanFcraDF[['CleanName', 'CleanState', 'fcrano', 'Registration']].tail()


# In[27]:


DarpanFcraDF[['CleanName', 'CleanState', 'fcrano', 'Registration']][DarpanFcraDF.fcrano.isnull() & DarpanFcraDF.Registration.notnull()]


# In[28]:


DarpanFcraDF['FCRA'] = DarpanFcraDF['Registration'].fillna(DarpanFcraDF['fcrano'])
DarpanFcraDF.info()


# ### Write csv

# In[29]:


DarpanFcraDF.to_csv('Darpan21FCRA.csv', index=False)
# DarpanFcraDF.to_excel('Darpan21FCRA.xlsx', index=False)


# #### not needed
# DarpanFcraDF.reset_index(inplace=True)
# DarpanFcraDF = DarpanFcraDF.rename(columns = {'index':'new column name'})

# # Make sets of IDs for all tags
# #### tags are "All", "FCRA", "URL", "MA1"

# In[30]:


TagsToIDVL = []
TagsToIDD = {}


# ### All NGO IDs

# In[31]:


AllIDV = set(DarpanFcraDF.UniqueID)


# In[32]:


TagsToIDVL.append({'tag': 'All', 'IDSet': AllIDV})
TagsToIDD['All'] = list(AllIDV)
len(AllIDV)


# ### FCRA number exists?

# In[33]:


FCRAV = set(DarpanFcraDF.UniqueID[DarpanFcraDF.FCRA.notnull()])


# In[34]:


TagsToIDVL.append({'tag': 'FCRA', 'IDSet': FCRAV})
TagsToIDD['FCRA'] = list(FCRAV)
len(FCRAV)


# ### URL exists?

# In[35]:


URLV = set(DarpanFcraDF.UniqueID[DarpanFcraDF['ngo url'].notnull()])


# In[36]:


TagsToIDVL.append({'tag': 'URL', 'IDSet': URLV})
TagsToIDD['URL'] = list(URLV)
len(URLV)


# ### Major activities exists?

# In[37]:


MA1V = set(DarpanFcraDF.UniqueID[DarpanFcraDF['Major Activities1'].notnull()])


# In[38]:


TagsToIDVL.append({'tag': 'MajorActivities', 'IDSet': MA1V})
TagsToIDD['MA1'] = list(MA1V)
len(MA1V)


# ## Write csv for tags and IDs
# https://www.geeksforgeeks.org/how-to-save-a-python-dictionary-to-a-csv-file/

# In[39]:


field_names = ['tag', 'IDSet']
with open('TagsToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(TagsToIDVL)


# ## write json for tags and IDs
# https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/

# In[40]:


# TagsToIDD[tag] = [UniqueID]
with open("TagsToIDList.json", "w") as outfile: 
    json.dump(TagsToIDD, outfile)


# # Make reverse look up dictionaries for Issues, States and Districts

# Issues:
# "Agriculture,Environment & Forests,Health & Family Welfare,"
# States:
# "UTTAR PRADESH, testingswss, UTTAR PRADESH, testingswss, UTTAR PRADESH,"
# Need to strip, remove '' and 'testingswss' and dedupe.

# In[41]:


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
    


# In[42]:


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


# In[43]:


StatesL = list(StateDistToIDD.keys())
StatesSer = pd.Series(StatesL)

IssuesSer = pd.Series(list(IssueToIDD.keys()))


# ## write json for sets of NGOs in Issue, State and State, Dist
# https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/

# In[44]:


# IssueToIDD[issue] = [UniqueID]
with open("IssueToIDList.json", "w") as outfile: 
    json.dump(IssueToIDD, outfile)

# StateToIDD[state] = [UniqueID]
with open("StateToIDList.json", "w") as outfile: 
    json.dump(StateToIDD, outfile)

# StateDistToIDD[state][dist] = [UniqueID]
with open("StateDistToIDList.json", "w") as outfile: 
    json.dump(StateDistToIDD, outfile)


# ## Write csv for sets of NGOs by feature

# ### Write csv for sets of NGOs by issue

# In[45]:


IssueToIDVL = []
for issue in IssueToIDD:
    IssueToIDVL.append({'issue': issue, 'IDSet': IssueToIDD[issue]})

field_names = ['issue', 'IDSet']
with open('IssueToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(IssueToIDVL)


# ### Write csv for sets of NGOs by State

# In[46]:


StateToIDVL = []
for state in StateToIDD:
    StateToIDVL.append({'state': state, 'IDSet': StateToIDD[state]})

field_names = ['state', 'IDSet']
with open('StateToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(StateToIDVL)


# ### Write csv for sets of NGOs by State and Dist

# In[47]:


StateDistToIDVL = []
for state in StateDistToIDD:
    for dist in StateDistToIDD[state]:
        StateDistToIDVL.append({'state': state, 'dist': dist, 'IDSet': StateDistToIDD[state][dist]})

field_names = ['state', 'dist', 'IDSet']
with open('StateDistToIDV.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(StateDistToIDVL)


# # Filter NGOs

# ## Select Issues

# In[48]:


IssuesSer


# In[50]:


selection = input("Select index of (preferably) one issue (or indices of upto 3 Issues) you are interested in, separated by ',' ind1, ind2, ind3 from above list\n").split(',')

IDInIssuesV = set()
for ind in selection:
    print("Number of NGOs in Issue", IssuesSer[int(ind)], "=", len(IssueToIDD[IssuesSer[int(ind)]]))
    IDInIssuesV = IDInIssuesV.union(set(IssueToIDD[IssuesSer[int(ind)]]))
print("Number of NGOs in any of the Issues =", len(IDInIssuesV))


# ## Select Region (States or Districts in a State)

# In[55]:


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


# In[58]:


FinalV = IDInIssuesV.intersection(IDInRegionV)
print("Number of NGOs in Issues and region =", len(FinalV))


# ## Select tags

# In[59]:


FCRATag = str(input("Are you a looking to make a donation to an NGO in Foreign Currency?\n'1' for 'Yes' '0' for 'No'\n"))

FCRAReqV = AllIDV
if FCRATag == '1':
    FCRAReqV = FCRAV


# In[60]:


URLTag = str(input("Do you want to be able to explore the NGO's website?\n'1' for 'Yes' '0' for 'No'\n"))

URLReqV = AllIDV
if URLTag == '1':
    URLReqV = URLV


# In[61]:


MATag = str(input("Would you like to be able to see the NGO's description of Major Activities?\n'1' for 'Yes' '0' for 'No'\n"))

MAReqV = AllIDV
if MATag == '1':
    MAReqV = MA1V


# ## Final set

# In[62]:


FinalV = FinalV.intersection(FCRAReqV)
print("Number of filtered NGOs =", len(FinalV))


# In[63]:


FinalV = FinalV.intersection(URLReqV)
print("Number of filtered NGOs =", len(FinalV))


# In[64]:


FinalV = FinalV.intersection(MAReqV)
print("Number of filtered NGOs =", len(FinalV))


# # Show info for sample of 10

# In[66]:


FinalL = list(FinalV)
sampleL = random.sample(FinalL, 10)


# In[67]:


DarpanFcraDF.set_index("UniqueID", inplace=True)


# In[70]:


DarpanFcraDF.loc[sampleL][['Name', 'ngo url', 'Email', 'Mobile', 'Major Activities1', 'Secretary name', 'Secretary mobile', 'Secretary email']]


# In[ ]:




