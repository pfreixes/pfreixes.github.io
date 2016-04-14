---
layout: post
title: Building an invert index with Python sets.
---

Almost everybody has written about the Python [sets](https://docs.python.org/2/library/stdtypes.html#set) and a few
ones about the frozensets. Even that the literature is still too much pragmatic and it lacks of real examples to 
figure out daily problems, something that a Python coder practices almost unwittingly. Yesterday I had an Eureka
moment trying to find the right problem to show how *frozensets* can be used. This post shows how to build a full text
search engine through an [invert index](https://en.wikipedia.org/wiki/Inverted_index) using a few lines of Python and plenty
of memory RAM.

# The theory

An inverted index is fully used to implement full text search engines, at least the first document retrieval systems appeard many
years ago. The idea of the inverted index is process the words belonging to each document and create an entry, indexed in a sort way,
that looks to the proper document. A index colision means that two or more documents share the words used to build the index.

Once the index is created we can use the same index function to process the words given as a query params to retrieve those
documents that are related with the index entry. For instance, the following sentences are used as tweet entries of our
implementation:

{% highlight bash %}
$ cat tweets.txt
This is a tweet about python and linux
This is a tweet about python and windows
This is a tweet about python and linux and windows
This is a tweet about rust
This is a tweet about the languages such as python running in linux
{% highlight %}

A query composed by *Python* and *Windows* words would return just the second sentence. In the case presented we are relaxing the use of
boolean operands where we are going to use always *ANDs* between words.

# Frozensets as index function for the inverted index

(Frozensets)[https://docs.python.org/2/library/stdtypes.html#frozenset] are immutable sets and due its immutability are hasheable, this 
characteristics fits very well to be used as a dictionary keys.

In the inverted index case, as we mentioned before, each document is going to be processed with a index function that takes the words belonging
to the document to create the proper index entry. We are going to use the hash function of a frozenset as the inverted index function.
The following snippet shows few examples of the value got by the hash function: 

{% highlight python %}

>>> hash(frozenset(['foo']))
4047620867903992349
>>> hash(frozenset(['bar']))
-9113672416919086926
>>> hash(frozenset(['foo', 'bar']))
4955649761666739161
>>> hash(frozenset(['bar', 'foo']))
4955649761666739161

{% highlight %}

As you can notice the last two entries generate the same hash value, worth mentioning that sets/frozensets have no sense of the order. In the case of the
implementation shown is also a requirement, look up for documents with the *foo* and *bar* words irrespective of the order.

# Creating the index ready to be used by any search

Time and space are intimately coupled in terms of complexity, they usually are inversely proportional. This implementation chooses save in 
in terms of cost of search - not in the processing step - to then use more memory. This election was based on the preference to make an extensive use of the frozensets.

As we saw before the frozenset can be used to get an unique hash value for a bunch of words, we can take profit of that characteristic
creating as many entries to the inverted index as many unique combinations of words the document has. For example, the following snippet shows
how with a bit of *itertools* sauce we are able to generate all of these needed hash values.


{% highlight python %}

>>> from itertools import combinations
>>> words = "my name is Foo and surname Bar".split(" ")
>>> for c in map(lambda i: combinations(words, i), xrange(1, len(words) + 1)):
...     print list(c)
...
[('my',), ('name',), ('is',), ('Foo',), ('and',), ('surname',), ('Bar',)]
[('my', 'name'), ('my', 'is'), ('my', 'Foo'), ('my', 'and'), ('my', 'surname'), ....

{% highlight %}

The itertools (combinations)[https://docs.python.org/2/library/itertools.html#itertools.combinations] helps us to create all of
needed values to be used as input of the inverted index function.

# Resolving positive words and negative words in a query

In the previous section we have seen how the inverted index key space is populated each time that a new document is inserted, but what value
will be used for each key?. 

The documents by them self are stored as elements in a list and the positions are used as pointers, hereby the implementation uses the 
positions as a way to identify and look up a document. Each value regarding a key of the inverted index stores a *set* with all of the
document pointers. For example the following snippet shows an example of how documents are index and stored to at last be linked between 
both data structures:

{% highlight python %}

>>> l = ['Hi my name is Foo and my surname is Bar']
>>> d = { frozenset(['Foo', 'Bar']): set([0]), frozenset(['Foo', 'Bar', 'surname']): set([0]) }
>>> d[frozenset(['Foo', 'Bar'])]
set([0])
{% highlight %}

As we can see each entry of the inverted index is in fact a *set*, it means that we are able to do bitwise operations between 
different entries. To get all of these documents that contain a certain words and not other ones it is a cinch.

# The implementation

The following snippet shows the final implementation putting all together. The *TextSearchIndex* publishes a interface
to add new documents and then find them by one or many words. The find interface is used to retrieve those documents
that contain the desired words regarding either the positive or negative ones.

{% highlight python %}

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

{% highlight %}

As an example we used a tweets corpus to search the tweets that have the have the words *python* and *linux* but not those tweets that have the word
*windows*,

{% highlight bash %}
$ cat tweets.txt | ./text_search_index.py python linux -windows
Entry found: This is a tweet about python and linux

Entry found: This is a tweet about the languages such as python running in linux
{% highlight %}
