import bisect
import PyICU
import struct
import socket
import numpy as np
import unidecode
import random
import re
import pickle

from interval import *

class dicotomix:

    # wordsAbs contains the (right) abscissa of words.
    # wordsSpell stores the spelling of words.
    # curr is the stack of visited intervals
    # the current state in self.curr[-1]
    # currentWordIndex is the stack of visited words
    # the current word is currentWordIndex[-1]
    def __init__(self):
        self.curr = [interval(0.0,1.0)]
        self.currentWordIndex = []
        self.cumulativeFreq = 0
        self.wordsAbs = []
        self.wordsSpell = []
        self.epsilon = 1 / 50 # randomized interval length
        #self.init_words2(dict_name,freq)

    # Load the dictionary with frequencies when structured
    # as in lexique_complet.csv
    # It's a bit hard coded, sorry for that
    def loadDictionary(self, dict_name):
        file = open(dict_name,"r")
        lines = file.read()
        lines = list(filter(lambda x: x != '', lines.split("\n")))
        frequencies = {}
        for line in lines[1:]:
            parameters = list(filter(lambda x: x!='', line.split(";")))

            word = self.removeApostropheEnd(parameters[0])
            freq = np.float128(parameters[-1])
            if not word in frequencies:
                frequencies[word] = freq
            else:
                frequencies[word] += freq

        dico = []
        for word in frequencies:
            dico.append((word, self.removeDash(word), frequencies[word]))

        collator = PyICU.Collator.createInstance(PyICU.Locale('fr_FR.UTF-8'))
        dico.sort(key = lambda x: collator.getSortKey(x[1]))

        cumulativeFreq = np.float128(0.0)
        self.wordsAbs.append(0.0)
        for word in dico:
            self.wordsSpell.append(word[0])
            cumulativeFreq += np.float128(word[2])
            self.wordsAbs.append(cumulativeFreq)
        self.wordsAbs = np.array(self.wordsAbs) / cumulativeFreq
        print(self.wordsAbs)

        file.close()

        #tmpF = open("outputDico.txt", "w")
        #for w in dico: tmpF.write(w[0] + "\n")
        #tmpF.close()

        #print(self.wordsAbs)
        #self.restart()
        #self.wordsAbs = list(map(lambda x: float(x)/float(cumulativeFreq),self.wordsAbs))

    # Remove accents from a string
    def removeAccents(self, word):
        return unidecode.unidecode(word)

    # Remove dashes and apostrophes from a string
    def removeDash(self, word):
        return re.sub(r"[' .-]+", r"", word)

    # Remove apostrophes at the end of a word
    def removeApostropheEnd(self, word):
        if word[-1] == "'":
            return word[:-1]
        else:
            return word

    # Used in order to efficiently find which word corresponds to
    # the current search interval
    def findIndex(self, cursor):
        i = bisect.bisect_right(self.wordsAbs, cursor)
        if i < 0:
            raise ValueError
        return i-1

    # Give a word corresponding to the current search interval:
    # a word close to the mid abcisse to wich is added a small random bias
    def getWord(self):
        mid = self.curr[-1].mid()
        randomization = random.uniform(-1, 1) * self.epsilon
        cursor = mid + self.curr[-1].length() * randomization
        self.currentWordIndex.append(self.findIndex(cursor))
        return self.wordsSpell[self.currentWordIndex[-1]] # Line to remove soon

    # Give the words corresponding to the interval bound
    def getWordsBound(self):
        i_word_beg = self.findIndex(self.curr[-1].beg)
        i_word_end = self.findIndex(self.curr[-1].end)
        if i_word_end >= len(self.wordsSpell):
            i_word_end = -1
        return self.wordsSpell[i_word_beg], self.wordsSpell[i_word_end]

    # Give the common prefix of bounds without accent
    def boundPrefix(self):
        w_beg,w_end = self.getWordsBound()
        w_beg = self.removeAccents(w_beg)
        w_end = self.removeAccents(w_end)
        k = 0
        for i in range(min(len(w_beg),len(w_end))):
            if w_beg[i] != w_end[i]:
                break
            k += 1
        return k

    #If our seeking interval is included
    #in a word interval it's over, we wont find it :(
    def isFinished(self):
        i_word_beg = self.findIndex(self.curr[-1].beg)
        i_word_end = self.findIndex(self.curr[-1].end)
        return i_word_end <= i_word_beg

    # Compute the interval length of word wrt its index
    def wordLength(self, index):
        return self.wordsAbs[index+1] - self.wordsAbs[index]

    # Does the left operation
    def goLeft(self):
        midIndex = self.currentWordIndex[-1]
        correction = self.wordLength(midIndex-1) / 100 # to avoid the "Existence" problem
        leftAbs = self.wordsAbs[midIndex] - correction
        self.curr.append(self.curr[-1].leftPart(leftAbs))
        myd.getWord()
        return self.isFinished()

    # Does the right operation
    def goRight(self):
        rightIndex = self.currentWordIndex[-1] + 1
        correction = self.wordLength(rightIndex) / 100 # to avoid the "Existence" problem
        rightAbs = self.wordsAbs[rightIndex] + correction
        self.curr.append(self.curr[-1].rightPart(rightAbs))
        myd.getWord()
        return self.isFinished()

    # Does the discard operation, remove current state
    def discard(self):
        if len(self.curr) > 1:
            self.curr = self.curr[:-1]
            self.currentWordIndex = self.currentWordIndex[:-1]

    # renitialize the word research
    def restart(self):
        self.curr = [interval(0.0,1.0)]
        self.currentWordIndex = []
        myd.getWord()

    # Test the method on a given word
    # it gives back the number of steps
    def testWord(self, targetWord):
#        print(self.curr)
#        print(self.getWord())
        proposedWord = self.getWord()

        targetWord = self.removeDash(targetWord)
        proposedWord = self.removeDash(proposedWord)

        if proposedWord == targetWord:
            return (True, 0)

        if self.isFinished():
            return (False, 0)

        to_cmp = [proposedWord, targetWord]

        collator = PyICU.Collator.createInstance(PyICU.Locale('pl_PL.UTF-8'))
        to_cmp.sort(key=collator.getSortKey)

        if targetWord == to_cmp[0]:
            self.goLeft()
        else:
            self.goRight()

        res = self.testWord(targetWord)
        return (res[0], 1+res[1])

    # gives back the mean number of trials over the whole dictionary
    # TODO: problem with finding the last word ([:-1] l.167)
    def testAll(self):
        d = {}
        m = 0
        self.restart()
        count = 0
        for w in self.wordsSpell[:-1]:
            res = self.testWord(w)
            if res[1] not in d:
                d[res[1]] = []


            d[res[1]].append(w)
            self.restart()
            if not res[0]:
                print("Error occurs with word: "+w)
                return
            m += res[1]
            count += 1

        print("pickle")
        pickle.dump(d, open("deep2word", "wb"))
        return float(m)/len(self.wordsSpell)



myd = dicotomix()
myd.loadDictionary("LexiqueCompletNormalise.csv")
#myd.testAll()
#exit(1)
myd.getWord()

# Communication routine
def send(conn, w, prefix):
    print("Sent data: "+w+", "+str(prefix))
    print(myd.getWordsBound())

    #conn.send(bytes(dico[beg]+","+dico[get_mid()]+","+dico[end-1], 'utf-8'))
    word = w.encode('utf8')
    conn.send(struct.pack(">I", len(word)))
    conn.send(word)
    conn.send(struct.pack(">I", prefix))

#print(myd.testWord("abandonneur"))
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    print(len(myd.currentWordIndex))
    cmd = conn.recv(BUFFER_SIZE)
    if not cmd: break
    print("received data:", cmd[0])

    if cmd[0] == 1:
###     Le mot choisi est : myd.wordsSpell[myd.currentWordIndex[-1]])
        myd.restart()
    if cmd[0] == 2:
        myd.goLeft()
    if cmd[0] == 3:
        myd.goRight()
    if cmd[0] == 4:
        myd.discard()

    send(conn,myd.wordsSpell[myd.currentWordIndex[-1]], myd.boundPrefix())

conn.close()
