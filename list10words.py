import pickle
from random import randint
from subprocess import call

depth2word = pickle.load(open("depth2word", "rb"))
for i in [2,3,4,5,7,8,9,11,13]:
	nbWord = len(depth2word[i])
	chosenWord = randint(0,nbWord - 1)
	print(depth2word[i][chosenWord])
