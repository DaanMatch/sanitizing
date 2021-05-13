# MyNLPConstants.py
""" Punctuations to be removed
    Stop words (pre-stemming)
    Output statements
    color list for figures
"""

PunctuationS = '''~!@#$%^&*()_+`-={}|[]\:";’'‘<>?,./'"–'''

# Some frequently occuring words removed from list via Zipf plot
# and 'we','did', how' and 'why' added
# Mostly constant, updated at some cadence to be determined

SomeStopWordsV = set(['the', 'of', 'a', 'is', 'to', 'in', 'and', 'be', \
    'that', 'as', 'can', 'it', 'or', \
    'on', 'an', 'we', 'how', 'why', 'did'])

# my_print statements
YourQS = "Your question:"
NoCloseMatchS = "No close matches found in the Knowledge Base, would you like to ask a Human Tutor?"
SelectOptionS = "From the following list, please select the question that best matches yours:\n"
NoMatchS = "No matches found in the Knowledge Base, would you like to ask a Human Tutor?"
NoneAboveS = "None of the Above: Ask a Human Tutor"

colorL = ['g', 'orange', 'r', 'm', 'b', 'c', 'y']
