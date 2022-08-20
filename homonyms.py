from collections import defaultdict
import string
import os.path
import httpx
import json
from copy import copy
import nltk
import shutil

VOEWLS = [
    "AA", # vowel
    "AE", # vowel
    "AH", # vowel
    "AO", # vowel
    "AW", # vowel
    "AY", # vowel
    "EH", # vowel
    "ER", # vowel
    "EY", # vowel
    "IH", # vowel
    "IY", # vowel
    "OW", # vowel
    "OY", # vowel
    "UH", # vowel
    "UW", # vowel
]

CONSONANTS = [
    "B", # stop
    "CH", # affricate
    "D", # stop
    "DH", # fricative
    "F", # fricative
    "G", # stop
    "HH", # aspirate
    "JH", # affricate
    "K", # stop
    "L", # liquid
    "M", # nasal
    "N", # nasal
    "NG", # nasal
    "P", # stop
    "R", # liquid
    "S", # fricative
    "SH", # fricative
    "T", # stop
    "TH", # fricative
    "V", # fricative
    "W", # semivowel
    "Y", # semivowel
    "Z", # fricative
    "ZH", # fricative
]


def is_vowel(sound):
    return any(sound.startswith(vowel) for vowel in VOEWLS)


def num_vowels(pronunciation):
    vowels = 0
    for sound in pronunciation:
        if is_vowel(sound):
            vowels += 1
    return vowels


def consonants_in(pronunciation):
    return [sound for sound in pronunciation if sound in CONSONANTS]


def remove_stress(pronunciation):
    sounds = []
    for sound in pronunciation:
        if is_vowel(sound):
            sound = sound[:-1]
        sounds.append(sound)
    return tuple(sounds)


CMUDICT = nltk.corpus.cmudict.dict()


def main():
    with open('output/main.words.json') as infile:
        words = json.load(infile)

    words_by_pronunciation = defaultdict(lambda: set())

    for word in words:
        if word not in CMUDICT:
            continue

        pronunciations = CMUDICT[word]
        for pronunciation in pronunciations:
            pronunciation = remove_stress(pronunciation)
            words_by_pronunciation[pronunciation].add(word)

    for pronunciation, words in words_by_pronunciation.items():
        if len(words) > 1:
            print(' '.join(pronunciation).ljust(30), words)


if __name__ == '__main__':
    main()

