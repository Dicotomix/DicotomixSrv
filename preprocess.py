# coding=utf-8
"""
Text preprocessing + bigrams generator

Sample usage:
python preprocess.py name-of-the-text-file

cfreq_2gram[last_word].most_common() <- it will return the word which is most likely to come afterwards
"""


import re
import nltk
import sys

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
    cfreq_2gram = nltk.ConditionalFreqDist(bg)




