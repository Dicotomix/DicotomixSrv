import pickle
import os
from Prediction import Prediction

def feed(fileFood):
	if os.path.isfile(fileFood):
		if os.path.isfile('feed.p'):
			predictions = pickle.load(open('feed.p', 'rb'))
			newPredictions = Prediction(fileFood)
			predictions = predictions + newPredictions
			print(predictions.bigram)
			pickle.dump(predictions, open('feed.p', 'wb'))
		else:
			predictions = Prediction(fileFood)
			pickle.dump(predictions, open('feed.p', 'wb'))
