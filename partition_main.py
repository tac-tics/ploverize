from copy import copy
from pathlib import Path
from collections import defaultdict
import sys
import json
import string
import shutil
import os.path

import nltk

import lib.orthography as orthography
import lib.outlines_extended as outlines_extended
import lib.outline
from lib.load import (
    load_net_dictionary,
    load_main_dictionary,
    load_lapwing_dictionary,
    save_dictionary,
    load_dictionary_path,
)


CMUDICT = nltk.corpus.cmudict.dict()
word_letters = [l for l in string.ascii_letters] + ["'", "-", " ", "."]


def has_punctuation(word):
    return not all(ch in word_letters for ch in word)
#    return any(ch in word for ch in '.,?/:;[]^&%$#@!(){}<>')

def is_affix(word):
    return word.startswith('{^') or word.endswith('^}')


def is_proper_noun(word):
    allowed = ["I", "I'll", "I'm", "I'd", "I've"]
    has_uppercase_letter = any(ch in string.ascii_uppercase for ch in word)
    contains_allowed_word = any(p == w for p in word.split(' ') for w in allowed)
    return has_uppercase_letter and not contains_allowed_word


def is_numeric(word):
    return any(digit in word for digit in string.digits)


def can_pronounce(word):
    return word in CMUDICT


SUFFIXES = [
    "'ll",
    "'s",
    "'ve",
    "n't",

    'ing',
#    'ed',
#    'er',
#    'ers',
#    'ly',
#    's',
#    'ier',

#    "le",
#    "or",
#    'ability',
#    'able',
#    'al',
#    'ary',
#    'ation',
#    'ble',
#    'bly',
#    'cal',
#    'cy',
#    'ial',
#    'ian',
#    'ibility',
#    'ic',
#    'ically',
#    'in',
#    'iness',
#    'ion',
#    'is',
#    'ism',
#    'ist',
#    'ity',
#    'ive',
#    'l',
#    'lar',
#    'less',
#    'ment',
#    'ness',
#    'ry',
#    'ship',
#    'tation',
#    'tion',
#    'tive',
#    'tory',
#    'ty',
#    'uous',
#    'y',
]


def partition_main(main_dictionary):
    print('* Partitioning Main Dictionary')

    words = set(main_dictionary.values())

    letters = set(w for w in words if len(w) == 1 and w != 'a' and w != 'I')
    words = words.difference(letters)
    save_dictionary('output/main.letters', sorted(letters))
    print('Created main.letters')

    affixes = set(w for w in words if is_affix(w))
    words = words.difference(affixes)
    save_dictionary('output/main.affixes', sorted(affixes))
    print('Created main.affixes')

    punctuation = set(w for w in words if has_punctuation(w))
    words = words.difference(punctuation)
    save_dictionary('output/main.punctuation', sorted(punctuation))
    print('Created main.punctuation')

    # How many of these have a Wikipedia page?
    proper_nouns = set(w for w in words if is_proper_noun(w))
    words = words.difference(proper_nouns)
    save_dictionary('output/main.proper', sorted(proper_nouns))
    print('Created main.proper')

    multiword = set(w for w in words if ' ' in w)
    words = words.difference(multiword)
    save_dictionary('output/main.multiword', sorted(multiword))
    print('Created main.multiword')

    numeric = set(w for w in words if is_numeric(w))
    words = words.difference(numeric)
    save_dictionary('output/main.numeric', sorted(numeric))
    print('Created main.numeric')

    cant_pronounce = set(w for w in words if not can_pronounce(w))
    words = words.difference(cant_pronounce)
    save_dictionary('output/main.cant_pronounce', sorted(cant_pronounce))
    print('Created main.cant_pronounce')

    inflections = set()

    for word in sorted(words, key=lambda w: (len(w), w)):
        for suffix in SUFFIXES:
            inflected_word = orthography.combine(word, suffix)
            if inflected_word in words:
                inflections.add(inflected_word)

    save_dictionary('output/main.inflections', sorted(inflections))
    words = words.difference(inflections)
    print('Created main.inflections')

    save_dictionary('output/main.words', sorted(words))
    print('Created main.words')

    new_dictionary = {}
    for outline, word in main_dictionary.items():
        if word in words:
            new_dictionary[outline] = word

    return new_dictionary



def main():
    main_dictionary = load_main_dictionary()
    partition_main(main_dictionary)


if __name__ == "__main__":
    main()

