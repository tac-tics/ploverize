from collections import defaultdict
import string
import os.path
import httpx
import json
from copy import copy
import nltk
import shutil

VOWELS = [
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
    return any(sound.startswith(vowel) for vowel in VOWELS)


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


def get_initial(pronunciation):
    result = []
    for sound in pronunciation:
        if is_vowel(sound):
            break
        result.append(sound)
    return result


def get_vowel(pronunciation):
    result = []
    for sound in pronunciation:
        if is_vowel(sound):
            result.append(sound)
    return result


def get_final(pronunciation):
    result = []
    at_final = False
    for sound in pronunciation:
        if at_final and not is_vowel(sound):
            result.append(sound)
        if is_vowel(sound):
            at_final = True
    return result

INITIAL_TO_OUTLINE = {
    'B': 'PW',
    'B L': 'PWHR',
    'B R': 'PWR',
    'CH': 'KH',
    'D': 'TK',
    'D R': 'TKR',
    'DH': 'SKWR',
    'F': 'TP',
    'F L': 'TPHR',
    'F R': 'TPR',
    'G': 'TKPW',
    'G L': 'TKPWHR',
    'G R': 'TKPWR',
    'HH': 'H',
    'JH': 'SKWR',
    'K': 'K',
    'K L': 'KL',
    'K R': 'KR',
    'K W': 'KW',
    'L': 'L',
    'M': 'PH',
    'N': 'TPH',
    'P': 'P',
    'P L': 'PHR',
    'P R': 'HR',
    'R': 'R',
    'S': 'S',
    'S K': 'SK',
    'S K R': 'SKR',
    'S K W': 'SKW',
    'S L': 'SHR',
    'S M': 'SPH',
    'S N': 'STPH',
    'S P': 'SP',
    'S T': 'ST',
    'S T R': 'STR',
    'S W': 'SW',
    'SH': 'SH',
    'T': 'T',
    'T R': 'TR',
    'T W': 'TW',
    'TH': 'TH',
    'TH R': 'THR',
    'V': 'SR',
    'V Y': 'SR',
    'W': 'W',
    'Y': 'KWR',
    '': '',
}

VOWEL_TO_OUTLINE = {
    "AA": 'A',
    "AE": 'A',
    "AH": 'A',
    "AO": 'OU',
    "AW": 'AU',
    "AY": 'AOEU',
    "EH": 'E',
    "ER": 'ER',
    "EY": 'AEU',
    "IH": 'EU',
    "IY": 'AOE',
    "OW": 'OU',
    "OY": 'OEU',
    "UH": 'AO',
    "UW": 'AOU',
}

FINAL_TO_OUTLINE = {
    'B': 'B',
    'CH': 'FP',
    'D': 'D',
    'DH': '?',
    'F': 'F',
    'F T': 'FT',
    'G': 'G',
    'JH': '?',
    'K': 'BG',
    'K S': 'BGS',
    'K T': 'BGT',
    'L': 'L',
    'L B': '?',
    'L D': 'LD',
    'L F': '?',
    'L K': '?',
    'L P': '?',
    'L S': 'LS',
    'L T': 'LT',
    'M': 'PL',
    'M P': '?',
    'N': 'PB',
    'N CH': '?',
    'N D': 'PBD',
    'N JH': '?',
    'N S': 'PBS',
    'N T': 'PBT',
    'N TH': '?',
    'NG': 'PBG',
    'NG K': 'PBG',
    'P': 'P',
    'R': 'R',
    'R CH': '?',
    'R D': 'RD',
    'R K': 'RBG',
    'R M': 'RPL',
    'R N': 'RPB',
    'R P': 'RP',
    'R S': 'RS',
    'R T': 'RT',
    'R TH': '?',
    'S': 'S',
    'S T': 'FT',
    'SH': '?',
    'T': 'T',
    'TH': '?',
    'V': 'F',
    'Z': 'Z',
    '': '',
}

def create_outline(initials, vowels, finals):
    outline = []
    outline.append(INITIAL_TO_OUTLINE.get(' '.join(initials), '?'))
    for ch in vowels:
        ch = ch[:-1] # strip off the stress
        outline.append(VOWEL_TO_OUTLINE.get(ch, '?'))
    outline.append(FINAL_TO_OUTLINE.get(' '.join(finals), '?'))

    return ''.join(outline)



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
        if len(pronunciations) > 1:
            continue

        pronunciation = pronunciations[0]

#        if word not in ['bat', 'cat', 'rat']: continue
        if num_vowels(pronunciation) == 1:
            if is_stem(word):
                outline = outlines_by_word[word]
                if len(outline) == 1:
                    outline = outline[0]
                else:
                    outline = ' '.join(outline)

                initials = get_initial(pronunciation)
                vowels = get_vowel(pronunciation)
                finals = get_final(pronunciation)

#                print(' '.join(finals))

                outline = create_outline(initials, vowels, finals)

                if '?' in outline: continue

                if (outline in lapwing_dictionary and lapwing_dictionary[outline] == word):
                    continue

                print(word.ljust(20), outline.ljust(20), ' '.join(pronunciation))
                print(' '.join(initials), ':', ' '.join(vowels), ':', ' '.join(finals))
                print(outline)
                print()


if __name__ == '__main__':
    main()

