from pathlib import Path
import sys
from collections import defaultdict
import string
import os.path
import httpx
import json
import orthography
from copy import copy
import nltk
import shutil
import outlines_extended


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


def main():
    with open('rights.txt') as infile:
        rights = set(line.strip() for line in infile)

    dictionary = load_lapwing_dictionary()
    for outline, word in dictionary.items():





if __name__ == '__main__':
    main()
