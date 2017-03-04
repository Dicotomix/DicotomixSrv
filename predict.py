"""
Predict the next word based on the trained cfd-model.pickle

Usage:
python predict.py input_word

Output: the function returns the word which is most likely to come next
"""

import cPickle as pickle
import sys

def predict(prev_word):
    with open('cfd-model.pickle', 'rb') as pickle_file:
        model = pickle.load(pickle_file)

    return model[prev_word].most_common()[0][0]

if __name__ == "__main__":
    print predict(sys.argv[1])

