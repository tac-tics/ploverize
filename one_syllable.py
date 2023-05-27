from collections import defaultdict
import string
import os.path
import httpx
import json
import orthography
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

def load_net_dictionary(url):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    return load_net_dictionary(url)


def load_lapwing_dictionary():
    url = 'https://raw.githubusercontent.com/aerickt/steno-dictionaries/6a0e3c844aec96a3d11350ef7a189f1ef03b243f/lapwing-base.json'
    return load_net_dictionary(url)

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


CMUDICT = nltk.corpus.cmudict.dict()


def is_stem(word):
    if word.endswith('ed') and word[:-2] in CMUDICT:
        return False

    if word.endswith('ed') and word[:-1] in CMUDICT:
        return False

    if word.endswith('ied') and word[:-3] + 'y' in CMUDICT:
        return False

    if word.endswith('ed') and word[-3] == word[-4] and word[:-3] in CMUDICT:
        return False

    if word.endswith('s') and word[:-1] in CMUDICT:
        return False

    if word.endswith("'s"):
        return False

    if word.endswith("s'"):
        return False

    if '.' in word:
        return False

    if word.endswith('ing') and word[:-3] in CMUDICT:
        return False

    return True


def main():
    lapwing_dictionary = load_lapwing_dictionary()

    outlines_by_word = defaultdict(lambda: [])
    for outline, word in lapwing_dictionary.items():
        outlines_by_word[word].append(outline)

    with open('words/basic_english_800.txt') as infile:
        words = [line.strip() for line in infile.readlines()]

    for word in words:
        if word == 'I':
            continue

        pronunciations = CMUDICT[word]
        pronunciation = pronunciations[0]
        if num_vowels(pronunciation) == 1:
            if is_stem(word):
                outline = outlines_by_word[word]
                if len(outline) == 1:
                    outline = outline[0]
                else:
                    outline = ' '.join(outline)
                print(f'    "{outline}": "{word}",')


if __name__ == '__main__':
    main()
