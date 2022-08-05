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

def split_outline_while(outline, allowed):
    for i, ch in enumerate(outline):
        if ch not in allowed:
            break

    return outline[:i], outline[i:]


LEFT_SIDE = 'TPHSKWR'
MIDDLE_SIDE = 'AO*EU'
RIGHT_SIDE =  'FPLTDRBGSZ'

assert split_outline_while('TPHER', LEFT_SIDE) == ('TPH', 'ER')
assert split_outline_while('ER', MIDDLE_SIDE) == ('E', 'R')


def split_outline(outline):
    left, rest = split_outline_while(outline, LEFT_SIDE)
    middle, right = split_outline_while(rest, MIDDLE_SIDE + '-')
    return left, middle.replace('-', ''), right


assert split_outline('TPHER') == ('TPH', 'E', 'R')
assert split_outline('TPH-R') == ('TPH', '', 'R')
assert split_outline('TPHA*RTZ') == ('TPH', 'A*', 'RTZ')


def make_pseudooutline(outline):
    left, middle, right = split_outline(outline)

    #  TPH
    # SKWR

    LEFT_REPLACEMENTS = [
        ('TPH', 'N'),
        ('TP', 'F'),
        ('TKPW', 'G'),
        ('TK', 'D'),
        ('TH', 'Th'),
        ('SR', 'V'),
        ('SKWR', 'J'),
        ('SH', 'Sh'),
        ('PW', 'B'),
        ('PH', 'M'),
        ('KWR', 'Y'),
        ('KW', 'Qu'),
        ('KP', 'X'),
        ('KH', 'Ch'),
        ('HR', 'L'),
    ]

    RIGHT_REPLACEMENTS = [
        ('T', 'Th'),
        ('RB', 'Sh'),
        ('FRP', 'Mp'),
        ('PL', 'M'),
        ('PLT', 'Ment'),
        ('PBLG', 'J'),
        ('PBG', 'Nk'),
        ('PBG', 'Ng'),
        ('PB', 'N'),
        ('LG', 'Lk'),
#        ('LG', 'Lch'),
        ('GS', 'Tion'),
        ('FRPB', 'Rch'),
        ('FRB', 'Rv'),
        ('FP', 'Ch'),
        ('BGS', 'Ks'),
        ('BG', 'K'),
    ]

    MIDDLE_REPLACEMENTS = [
        ('AOEU', 'Eye'),
        ('AOE', 'Ee'),
        ('AU', 'Aw'),
        ('AO', 'Oo'),
        ('AE', 'Ea'),
        ('OEU', 'Oy'),
        ('OU', 'Ow'),
        ('OE', 'Oe'),
        ('EU', 'I'),
    ]

    for before, after in LEFT_REPLACEMENTS:
        left = left.replace(before, after)

    for before, after in RIGHT_REPLACEMENTS:
        right = right.replace(before, after)

    for before, after in MIDDLE_REPLACEMENTS:
        middle = middle.replace(before, after)

    if not left and not middle:
        middle = '-'

    return left + middle + right

assert make_pseudooutline('TKPWRAOEPB') == 'GREeN'


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


def load_net_dictionary(url):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    return load_net_dictionary(url)


def save_dictionary(name, dictionary):
    filename = f'output/{name}.json'

    with open(filename, 'w') as outfile:
        json.dump(dictionary, outfile, indent=4, ensure_ascii=False)


def load_dictionary(name):
    filename = f'output/{name}.json'

    with open(filename) as infile:
        return json.load(infile)


CMUDICT = nltk.corpus.cmudict.dict()


def main():
    dictionary = load_main_dictionary()
    for outline, word in dictionary.items():
        if word not in CMUDICT:
            continue

        pronunciations = CMUDICT[word]
        pronunciation = pronunciations[0]

        if num_vowels(pronunciation) == 1:
            pseudooutline = make_pseudooutline(outline)
            print(pseudooutline, word, consonants_in(pronunciation))


#    for word, pronunciations in CMUDICT.items():
#        if num_vowels(pronunciations[0]) != 1:
#            continue
#
#        print(word.ljust(15), end='')
#        for i, pronunciation in enumerate(pronunciations):
#            if i == 0:
#                spaces = ''.ljust(15)
#            else:
#                spaces = ''.ljust(30)
#
#            print(spaces, pronunciation, consonants_in(pronunciation))
#


if __name__ == "__main__":
    main()

