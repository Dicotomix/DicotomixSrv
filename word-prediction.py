import pickle
import os.path
from nltk.util import bigrams
from nltk.probability import ConditionalFreqDist
import re

data = open('food', 'r')
text = data.read()
#stopWords = set(nltk.corpus.stopwords.words("french")) #List of french stopwords
tempBigrams = []
for sentence in re.split('\.|\?|!', text):
   #relevantWords = [w for w in re.sub(r',|;|:|"', '', sentence).lower().split() not in stopWords]
   relevantWords = [w for w in re.sub(r',|;|:|"', '', sentence).lower().split()]
   tempBigrams += list(bigrams(relevantWords))


if os.path.isfile('feed.p'):
   predictions = pickle.load(open('feed.p', 'rb'))
   predictions.update(tempBigrams)
else:
   predictions = ConditionalFreqDist(tempBigrams)

data.close()
pickle.dump(predictions, open('feed.p', 'wb'))
