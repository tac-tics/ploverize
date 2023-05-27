import sys
import orthography

import random
import httpx
import json

import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import words


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


INITIALS = {
    'CH': 'KH',
    'JH': 'SKWR',
    'HH': 'H',
    'DH': 'STH',
    'F': 'TP',
    'S': 'S',
    'SH': 'SH',
    'TH': 'TH',
    'V': 'SR',
    'Z': 'S',
#    'ZH':
    'L': 'HR',
    'R': 'R',
    'M': 'PH',
    'N': 'TPH',
#    'NG': 
    'W': 'W',
    'Y': '',
    'B': 'PW',
    'D': 'TK',
    'G': 'TKPW',
    'K': 'K',
    'P': 'P',
    'T': 'T',
}

VOWELS = {
    'AA': 'A',
    'AE': 'AE',
    'AH': 'U',
    'AO': 'AU',
    'AW': 'OU',
    'AY': 'AOEU',
    'EH': 'E',
    'ER': 'ER',
    'EY': 'AE',
    'IH': 'AOE',
    'IY': 'AOE',
    'OW': 'OE',
    'OY': 'OEU',
    'UH': 'U',
    'UW': 'AOU',
}



if __name__ == '__main__':
    main()
