from collections import defaultdict
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


def load_dictionary(name):
    filename = f'output/{name}.json'

    with open(filename) as infile:
        return json.load(infile)


def main():
    dictionary = load_dictionary('010.main')
    for outline, word in dictionary.items():
        strokes = outline.split('/')
        if len(strokes) == 1:
            print(outline, word)


if __name__ == "__main__":
    main()

