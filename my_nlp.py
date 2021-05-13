# my_nlp.py
""" nltk modules and some functions I've defined for NLP
"""

import copy
import math

# From https://pythonprogramming.net/stemming-nltk-tutorial/
import nltk

import numpy as np
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    print("Nltk punkt initialization complete please restart your application")
    exit ()
    
from nltk.stem import PorterStemmer
ps = PorterStemmer()

from nltk.tokenize import sent_tokenize, word_tokenize

from MyNLPConstants import *


# to remove punctuation
def depunctuate(strS):
    """From argument string, removes all puncuation symbols in 
        the constant string PunctuationS
    """
    for punc in PunctuationS:
        strS = strS.replace(punc, " ")
    return strS


# Depunctuate, lowercase and tokenize
def tokenize(txt):
    """depunctuates, lowercases and word-tokenizes the argument text string
    and returns a list of the tokens
    """
    Depunc = depunctuate(txt).lower()
    Tokens = word_tokenize(Depunc)
    
    return Tokens


# Tokenize, remove StopWords and stems
def stokenize(txt, StopWords):
    """tokenizes, removes Stop Words,
    stems the argument text string
    and returns a list of the stemmed tokens
    """
    Tokens = tokenize(txt)
    UnStopped = [t for t in Tokens if t not in StopWords]
    Stokens = [ps.stem(w) for w in UnStopped] # Stokens = Stemmed Tokens, list of all stokens in the txt
    
    return Stokens


# Confusion matrix
def confusion_matrix(documentV, targetV, testV):
    """ Given the universal (document) set, the target set 
        and the test set, 
        calculates the confusion matrix of (number of) 
        TP = True Positives
        FP = False Positives
        FN = False Negatives and 
        TN = True Negatives
        documentV includes the union with both targetV and testV
    """
    DocSize = len(documentV)
    TgtSize = len(targetV)
    TstSize = len(testV)
    
    TruePositiveV = targetV.intersection(testV)

    TP = len(TruePositiveV)
    FP = TstSize - TP
    FN = TgtSize - TP
    TN = DocSize - TgtSize - FP

    return TP, FP, FN, TN


def lndor(TP, FP, FN, TN):
    """ln(diagnostic odds ratio) for a confusion matrix
    """
    if FP == 0 or FN == 0:
        out = 10.
    elif TP == 0 or TN == 0:
        out = -10.
    else:
        out = math.log((TP * TN) / (FP * FN))

    return out

    
def angleDOR(TP, FP, FN, TN, priorOddsRatio = 1):
    """ angleDOR = arctan(1/lndor) for a confusion matrix, in radians in [0, pi]
        priorOddsRatio is the relative odds ratio corresponding to 
        the prior probability of the target, derived from count
    """
    if FP == 0 or FN == 0:
        out = 0.
    elif TP == 0 or TN == 0:
        out = math.pi
    else:
        lnDOR = lndor(TP, FP, FN, TN)
        lnOdds = lnDOR + math.log(priorOddsRatio)
        if lnOdds < 0:
            out = math.atan(1 / lnOdds) + math.pi
        else:
            out = math.atan(1 / lnOdds)

    return out


def stokenizeKBD(TargetQuestionsD, StopWords):
    """ stokenize all Target questions and answers in KB
        input TargetQuestionsD = {i : {'question': , 'answer': , 'resource': , "matched questions": [], 'count': }}
        for each target Q: 
            for its matching questions (includes the target question when added to dict)
                construct list of stokens
                add 'mq stokens' element to dictionary 
                add 'ans stokens' element to dictionary 
        Modifies
            TargetQuestionsD = {i : {'question': , 'answer': , 'resource': , "matched questions": [], 'count': , 'mq stokens': [], 'ans stokens': []}}
    """
    for i in TargetQuestionsD:
        mqstokens = [] 
        for mq in TargetQuestionsD[i]["matched questions"]:
            mqstokens.extend(stokenize(mq, StopWords)[:])
        TargetQuestionsD[i]["mq stokens"] = mqstokens[:]

        TargetQuestionsD[i]["ans stokens"] = stokenize(TargetQuestionsD[i]["answer"], StopWords)[:]
        
    return "TargetQuestionsD = {i : {'question': , 'answer': , 'resource': , 'matched questions': [], 'count': , 'mq stokens': [], 'ans stokens': []}}"


def intent_of_text_LnDOR(ChapterTextS, TargetQuestionsD, TestS, StopWords):
    """ Intent based on Log Diagnostic Odds Ratio
        Includes lndor for AntiTgt words
        Calculates intent of learner test string vis-a-vis targets in KB  questions
        Based on ln(Diagnostic Odds Ratio) = LnDOR:
            DOR = (TP * TN) / (FP * FN)
            IDOR = Inverse DOR = (FP * FN) / (TP * TN) is a distance function between sets,
            It is symmetric, positive definite \in [0, \infty)].
            It is also "scale invariant": 
                If either Target or test sets scales agnostically, the DOR remains the same.
        Define the angle between two sets angle = arctan(1/LnDOR) in top halfplane, 
        This may not be the angle corresponding to the above distance function.
        *** Do NOT use cosine similarity = math.cos(angle) as 'match %'       
        document = chapter text + test string + KB questions (with their matches) + KB answer
        !!! call to stokenizeKBD() changes targetQuestions dict!!!
    """
    
    # Chapter Text - stokenize
    StokensCT = stokenize(ChapterTextS, StopWords) 

    # Test question - stokenize
    StokensTest = stokenize(TestS, StopWords)

    # Knowledge Base Dict - stokenize
    KBD_structure = stokenizeKBD(TargetQuestionsD, StopWords)

    # List (because list is mutable, set is not) of all stokens in document
    StokensDoc = StokensCT[:] # from chapter text
    StokensDoc.extend(StokensTest[:]) # += Test string

    # extend list of stokens in Doc
    for i in TargetQuestionsD:
        StokensDoc.extend(TargetQuestionsD[i]["mq stokens"][:]) # += KB target [matched Q]s
        StokensDoc.extend(TargetQuestionsD[i]["ans stokens"][:]) # += KB answers
        
    StokensTestV = set(StokensTest)
    StokensDocV = set(StokensDoc)
    StokensAntiTgtV = StokensDocV
    
    # Complement of all targets
    for i in TargetQuestionsD:
        StokensAntiTgtV = StokensAntiTgtV.difference(set(TargetQuestionsD[i]["mq stokens"]))
        
    # calculate confusion matrix and DOR etc.
    LnDORD = {}
    # Anti Target
    TP, FP, FN, TN = confusion_matrix(StokensDocV, StokensAntiTgtV, StokensTestV) 
    LnDOR = lndor(TP, FP, FN, TN) 
    someAngle = angleDOR(TP, FP, FN, TN) 
    
    LnDORD["AntiTgt"] = {'lndor': LnDOR, 'theta': someAngle}

    # total occurences
    total_occ = 0
    for i in TargetQuestionsD:
        total_occ += TargetQuestionsD[i]['count']

    for i in TargetQuestionsD:
        StokensTgtV = set(TargetQuestionsD[i]["mq stokens"][:])

        TP, FP, FN, TN = confusion_matrix(StokensDocV, StokensTgtV, StokensTestV) 
        priorOR = TargetQuestionsD[i]['count'] / total_occ

        LnDOR = lndor(TP, FP, FN, TN) 
        someAngle = angleDOR(TP, FP, FN, TN, priorOR) 
        
        LnDORD[i] = {'lndor': LnDOR, 'theta': someAngle}
    # LnDORD = {i: {'lndor': , 'theta': }}, KB indices + "AntiTgt"

    return LnDORD


def ranked_KBQs(lndorD, n = 4, max_angle = math.pi/4):
    """Sort and select maximum n KB question indices in descending LnDOR order,
        only if they are less than max_angle from the testQ.
        Later, we can reduce the number of potential matches presented in the UI,
        if we see a low marginal likelihood of a match of the nth
    """

    KBIndexL = list(lndorD.keys()) # here 'keys' = KB indices + "AntiTgt"
    KBIndexL.sort(reverse = True, key = lambda i: lndorD[i]['lndor']) # here 'key' = sorting function

    LnDORRankedL = []
    for rank in range(n):
        try:
            kbi = KBIndexL[rank]
            if lndorD[kbi]['theta'] <= max_angle:
                LnDORRankedL.append(lndorD[kbi]) # {'lndor': , 'theta': }
                LnDORRankedL[rank]['KB index'] = kbi # add this element to the dictionary
            else:
                pass
        except IndexError:
            pass
    
    # List of n dictionaries [{'KB Index': , lndor': , 'theta': }] in descending order of ln(DOR)
    return LnDORRankedL




def theta_matrix(ChapterTextS, TargetQuestionsD, StopWords):
    """ angular distance matrix between KB questions
        Calculates the angular distance matrix between targets in KB questions
        Based on ln(Diagnostic Odds Ratio) = LnDOR:
        Define the angle between two sets theta_value = arctan(1/LnDOR), 
        document = chapter text + KB questions (with their matches) + KB answer
        !!!Call to stokenizeKBD()Changes targetQuestionsD !!!
    """
    
    # Chapter Text - stokenize
    StokensCT = stokenize(ChapterTextS, StopWords) 

    # Knowledge Base Dict - stokenize
    KBD_structure = stokenizeKBD(TargetQuestionsD, StopWords)
    # TargetQuestionsD = {i : {'question': , 'answer': , 'resource': , "matched questions": [], 'mq stokens': [], 'ans stokens': []}}

    # List (because list is mutable, set is not) of all stokens in document
    StokensDoc = StokensCT[:] # from chapter text

    # extend list of stokens in Doc to include matched question stokens and answer stokens
    for i in TargetQuestionsD:
        StokensDoc.extend(TargetQuestionsD[i]["mq stokens"][:]) # += KB target [matched Q]s
        StokensDoc.extend(TargetQuestionsD[i]["ans stokens"][:]) # += KB answers
        
    StokensDocV = set(StokensDoc)
    
    n = len(TargetQuestionsD)

    # Construct list of MQStokensV
    MQStokensSetL = []
    for i in np.arange(n):
        MQStokensSetL.append(set(TargetQuestionsD[i]["mq stokens"]))
    
    """ 
    Not working
    def thetaFn(i, j):
        Vi = MQStokensSetL[i]
        Vj = MQStokensSetL[j]
        TP, FP, FN, TN = confusion_matrix(StokensDocV, Vi, Vj)
        return angleDOR(TP, FP, FN, TN)
    print("This is ", thetaFn(3,4))
    thetaMat = np.fromfunction(lambda i, j: thetaFn(i, j), (n, n))
    """
    
    thetaMat = np.zeros((n, n))
    for i in np.arange(n):
        for j in np.arange(i+1, n):
            Vi = MQStokensSetL[i]
            Vj = MQStokensSetL[j]
            TP, FP, FN, TN = confusion_matrix(StokensDocV, Vi, Vj)
            thetaValue = angleDOR(TP, FP, FN, TN)
            thetaMat[i, j] = thetaValue
            thetaMat[j, i] = thetaValue

    return thetaMat











