import typing as t
from dataclasses import dataclass
import json

from collections import defaultdict
import string
import os.path
import httpx
import json
import orthography
from copy import copy
import nltk
import shutil


def load_net_dictionary(url):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

Stroke = str


@dataclass
class PrefixTree:
    children: t.Dict[Stroke, 'PrefixTree']
    word: t.Optional[str]

    @staticmethod
    def new():
        return PrefixTree(
            children={},
            word=None,
        )

    def add(self, outline, word):
        strokes = outline.split('/')
        self.add_by_strokes(strokes, word)

    def add_by_strokes(self, strokes, word):
        if len(strokes) == 0:
            self.word = word
        else:
            head = strokes[0]
            tail = strokes[1:]
            if head not in self.children:
                self.children[head] = PrefixTree.new()

            child = self.children[head]
            child.add_by_strokes(tail, word)

    def __getitem__(self, stroke):
        if stroke not in self.children:
            return None
        else:
            return self.children[stroke]

    def empty_trail(self):
        return PrefixTrail(
            pointer=self,
            previous=None,
            outline='',
        )

    def trail(self, outline):
        strokes = outline.split('/')
        trail = self.empty_trail()
        for stroke in strokes:
            trail = trail[stroke]

        return trail


@dataclass
class PrefixTrail:
    pointer: PrefixTree
    previous: t.Optional['PrefixTrail']
    outline: str

    def __getitem__(self, stroke):
        if stroke not in self.pointer.children:
            return None
        else:
            return PrefixTrail(
                pointer=self.pointer.children[stroke],
                previous=self,
                outline=self.outline + '/' + stroke,
            )

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.previous is None:
            return "(BASE)"
        else:
            return str(self.previous) + ' / ' + "(" + self.outline + " => " + (self.pointer.word or "None") + ")"

    def is_complete(self):
        if self.previous is None:
            return True
        else:
            if self.pointer.word is None:
                return False
            else:
                return self.previous.is_complete()
        


def from_dictionary(dictionary):
    tree = PrefixTree.new()
    for outline, word in dictionary.items():
        tree.add(outline, word)

    return tree

def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    return load_net_dictionary(url)


def main():
    dictionary = load_main_dictionary()
    tree = from_dictionary(dictionary)
#    trail = tree.empty_trail()

    for outline, word in dictionary.items():
        trail = tree.trail(outline)
        if not trail.is_complete():
            print(word, trail)


if __name__ == '__main__':
    main()
