import random
import httpx
import json

import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import words


cmudict = nltk.corpus.cmudict.dict()
words = set()

with open('output/dict_stripped.txt') as infile:
    for line in infile:
        word = line.strip()
        if word in cmudict:
            words.add(word)
        else:
            print(word)
