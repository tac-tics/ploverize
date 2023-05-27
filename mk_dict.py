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


def initial_dict():
    words = set()
    forbiddens = '{}^0123456789 .,;:()!=$&<>[]+*`?-#©é÷–—'


    for outline, word in load_main_dictionary().items():
        if any(c in word for c in forbiddens):
            continue

        if word != 'I' and word != word.lower():
            continue

        if len(word) == 1 and word not in ['a', 'I']:
            continue

        if word in ["'n'"]:
            continue

        words.add(word)


    return words


def remove_nonbase_words(words):
    new_words = set(words)
    with open('nonbase_words.txt') as infile:
        for line in infile:
            word = line.strip()
            if word in new_words:
                new_words.remove(word)

    return new_words


def remove_unpronouncable(words):
    new_words = set()

    cmudict = nltk.corpus.cmudict.dict()

    for word in words:
        if word in cmudict:
            new_words.add(word)

    return new_words


def main():
    words = initial_dict()
    words = remove_nonbase_words(words)
    words = remove_unpronouncable(words)

    cmudict = nltk.corpus.cmudict.dict()

    for word in sorted(words):
        print(word)


if __name__ == "__main__":
    main()
