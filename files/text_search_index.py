#!/usr/bin/env python
#
# A naive implementation of an inverted index using Python. The idea is use as many word permutations per 
# entry to save after as frozensets in a dictionary. Once the dictionary is populated the user can
# make queries looking for entries that have one or many words, mixing bitwise operators.
#
# The command recieves the entries as standar iput and then it applies over all entries the word filters
# given as arguments. Each argument means a word less these ones starting with a - character that will
# be used with the NOT operator.
#
# For example the following command will search for those entries that have the `python` and `linux` word
# and they dont have the `windows` word.
#
# $ cat tweets.txt | ./text_search_index.py python linux -windows 
#
# The entry file will split the entries using a \n character.
#
# Author : pfreixe@gmail.com
# Date: 2016-04

import sys

from itertools import combinations
from collections import defaultdict

class TextSearchIndex(object):

    def __init__(self):
        self._texts = []
        self._index = defaultdict(set)

    def add(self, text):
        """Index a new `text` to become searchable by all of its words permutations.

        :param text: str.
        """
        self._texts.append(text)

        words = [reduce(lambda word, s: word.strip(s), [word] + [' ', '\n', ',', '.', ':', ';']) for word in text.split(' ')]
        for c in map(lambda i: combinations(words, i), xrange(1, len(words) + 1)):
            for words in c:
                self._index[frozenset(words)].add(len(self._texts) - 1)

    def find(self, words):
        """ Return a iteartor with all index entries that have this words, otherwise
        return a None.

        :param words: list of strings
        """
        return self._index.get(frozenset(words), set())

    def entry(self, index):
        """ Return a text regarding a index given.

        :param index: int.
        """
        return self._texts[index]


def main():
    t = TextSearchIndex()
    map(lambda line: t.add(line), sys.stdin.readlines())

    try:
        all_words = set(sys.argv[1:])
    except IndexError:
        print "Give some word!"
        sys.exit(1)

    negative_words = set(filter(lambda word: word[0] == '-', all_words))
    positive_words = all_words - negative_words

    if not positive_words:
        print "Give some none negative word!"
        sys.exit(1)

    indexes_with_chances = t.find(positive_words)
    for word in negative_words:
        indexes_with_chances -= t.find([word[1:]])  # remove the first `-` character

    for index in indexes_with_chances:
        print "Entry found: {}".format(t.entry(index))

if __name__ == '__main__':
    main()
