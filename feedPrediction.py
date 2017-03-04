# -*- coding: utf-8 -*-
import pickle
import os
from Prediction import Prediction

def feed(fileFood):
	"""This function create an object to predict which word may come next and to store that object in a pickle file."""
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
