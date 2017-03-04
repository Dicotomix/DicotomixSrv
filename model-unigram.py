"""
The unigram-model built with gensim and the French wikipedia

Input: a word (eg. the previous input word)
Output: a list of the most similar words sorted in descending order

TODO: create a dataset to train a bi-gram or tri-gram model which better captures the sentence structure
"""

import gensim
import sys

#model = gensim.models.KeyedVectors.load_word2vec_format('wiki/wikifr.vec', binary=False, unicode_errors='ignore')
#model.save("model.pickle")

#print model.most_similar(positive=['soviet'])

word = sys.argv[1]
model = gensim.models.KeyedVectors.load("model.pickle")

list = []
list.append(word)

print model.most_similar(positive=list)