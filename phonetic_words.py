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


VOWELS = [
    'AA',
    'AE',
    'AH',
    'AO',
    'AW',
    'AY',
    'EH',
    'ER',
    'EY',
    'IH',
    'IY',
    'OW',
    'OY',
    'UH',
    'UW',
]

#CONSONANTS = [
#affricate CH
#affricate JH
#aspirate HH
#fricative DH
#fricative F
#fricative S
#fricative SH
#fricative TH
#fricative V
#fricative Z
#fricative ZH
#liquid L
#liquid R
#nasal M
#nasal N
#nasal NG
#semivowel W
#semivowel Y
#stop B
#stop D
#stop G
#stop K
#stop P
#stop T
#]


def is_single_syllable(pronunciation):
    return syllable_count(pronunciation) == 1


def syllable_count(pronunciation):
    vowel_count = 0
    for sound in pronunciation:
        if any(sound.startswith(vowel) for vowel in VOWELS):
            vowel_count += 1

    return vowel_count


def make_outline_dict(dictionary):
    result = {}
    for outline, word in dictionary.items():
        if word not in result:
            result[word] = []
        result[word].append(outline)
    return result


def initial_in_outline(outline):
    result = []
    for ch in outline:
        if ch in 'AEOU*':
            break
        else:
            result.append(ch)
    return ''.join(result)

def vowels_in_outline(outline):
    return ''.join(ch for ch in outline if ch in 'AEOU')


def vowels_in_syllable(pronunciation):
    vowels = []
    for sound in pronunciation:
        if any(sound.startswith(vowel) for vowel in VOWELS):
            vowels.append(sound[:-1])
    return vowels


def initial_in_syllable(pronunciation):
    initial = []
    for sound in pronunciation:
        if any(sound.startswith(vowel) for vowel in VOWELS):
            break
        else:
            initial.append(sound)
    return initial


VOWEL_MAP = {
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


def main():
    words = set()
    with open('output/dict.txt') as infile:
        for line in infile:
            word = line.strip()
            words.add(word)

    cmudict = nltk.corpus.cmudict.dict()
    main_dictionary = load_main_dictionary()
    outline_dict = make_outline_dict(main_dictionary)

    for word in sorted(words):
        pronunciation = cmudict[word][0]
        outline = outline_dict[word][0]
        if is_single_syllable(pronunciation):
            print(initial_in_outline(outline), initial_in_syllable(pronunciation), word)


if __name__ == "__main__":
    main()
