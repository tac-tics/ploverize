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


SUFFIXES = []
with open('suffix_list.txt') as infile:
    for line in infile:
        suffix = line[2:-2]
        if suffix:
            SUFFIXES.append(suffix)


def main():
    main_dictionary = load_main_dictionary()
    words = set(main_dictionary.values())
    base_words = set(words)

    for suffix in SUFFIXES:
        sys.stdout.flush()
        print('SUFFIX =', suffix, file=sys.stderr)
        for word in words:
            compound_word = orthography.combine(word, suffix)
            if orthography.combine(word, suffix) in words:
                print(f'{compound_word},{word},{suffix}')
                if compound_word in base_words:
                    base_words.remove(compound_word)

    print(len(words), file=sys.stderr)
    print(len(base_words), file=sys.stderr)

    for word in base_words:
        print(word)



if __name__ == "__main__":
    main()
