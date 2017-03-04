# coding=utf-8
"""
Text preprocessing + CFD generator

Sample usage:
python preprocess.py name-of-the-text-file

the CFD model will be stored in "cfd-model.pickle"


TODO: get the last word from UI and have a separate file which returns "cfd[last_word].most_common()"

"""

import re
import nltk
import sys
import cPickle as pickle

reload(sys)
sys.setdefaultencoding('utf8')

def preprocess_line(line):
    letters_only = re.sub("[^a-zàâçéèêëîïôûùüÿñæœA-Z]",
                      " ",
                      line )
    words = letters_only.lower().split()
    stops = set(nltk.corpus.stopwords.words("french"))
    meaningful_words = [w for w in words if not w in stops]
    return( " ".join( meaningful_words ))

def tokenize(line):
    tokens = nltk.word_tokenize(line)
    return nltk.bigrams(tokens)


if __name__ == "__main__":
    dataset = sys.argv[1]
    data = open(dataset)
    raw = data.read()
    prep = preprocess_line(raw)
    bg = tokenize(prep)
    cfd = nltk.ConditionalFreqDist(bg)

    with open("cfd-model.pickle", 'wb') as pickle_file:
        pickle.dump(cfd, pickle_file)

    #with open('cfd-model.pickle', 'rb') as pickle_file:
        #content = pickle.load(pickle_file)




