# -*- coding: utf-8 -*-
import os.path
import re

class Prediction:

	def __init__(self, fileFood=False):
		self.bigram = {}
		self.nbWords = 0

		if os.path.isfile(fileFood):
			data = open(fileFood, 'r')
			text = data.read()
			data.close()

			#stopWords = set(nltk.corpus.stopwords.words("french")) #List of french stopwords
			for sentence in re.split('\.|\?|!', text):
				#relevantWords = [w for w in re.sub(r',|;|:|"', '', sentence).lower().split() not in stopWords]
				relevantWords = [w for w in re.sub(r',|;|:|"', '', sentence).lower().split()]
				self.update(relevantWords)

	def update(self, words):
		n = len(words)
		for i in range(n):
			if i < n - 1:
				if words[i] in self.bigram:
					if words[i+1] in self.bigram[words[i]]:
						self.bigram[words[i]][words[i+1]] += 1
					else:
						self.bigram[words[i]][words[i+1]] = 1
				else:
					self.bigram[words[i]] = {words[i+1]: 1}
					self.nbWords += 1

	def __add__(self, pred2):
		result = Prediction()
		result.bigram = self.bigram
		result.nbWords = self.nbWords

		n = len(pred2.bigram)
		for word2 in pred2.bigram:
			for word3 in pred2.bigram[word2]:
				if word2 in result.bigram:
					if word3 in result.bigram[word2]:
						result.bigram[word2][word3] += 1
					else:
						result.bigram[word2][word3] = 1
				else:
					result.bigram[word2] = {word3: 1}
					result.nbWords += 1

		return result
	
	def nextWords(self, word, nbPredictions=1):
		"""This method returns the words more likely to follow the word "word"."""
		if word not in self.bigram or nbPredictions == 0:
			return False
		else:
			m = 1
			nextWordResult = []
			temp = dict(self.bigram[word])
			for i in range(nbPredictions):
				if temp != {}:
					nextWord = max(temp, key=temp.get)
					nextWordResult.append((nextWord,temp[nextWord]))
					del(temp[nextWord])
				else:
					return nextWordResult

			return nextWordResult
