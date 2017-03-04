import bisect
import PyICU
import struct 
import socket
import numpy as np
import unidecode
import random

from interval import *

class dicotomix:

    # wordsAbs contains the (right) abscissa of words.
    # wordsSpell stores the spelling of words.
    # curr is the stack of visited intervals
    # the current state in self.curr[-1]
    def __init__(self):
        self.curr = [interval(0.0,1.0)]
        self.s = 0
        self.wordsAbs = []
        self.wordsSpell = []
        self.epsilon = 1 / 100 # randomized interval length
        #self.init_words2(dict_name,freq)

    def restart(self):
        self.curr = [interval(0.0,1.0)]

    # Load the dictionary with frequencies when structured
    # as in lexique_complet.csv
    # It's a bit hard coded, sorry for that
    def loadDictionary(self,dict_name):
        file = open(dict_name,"r")
        lines = file.read()
        lines = list(filter(lambda x: x != '', lines.split("\n")))
        frequencies = {}
        for line in lines[1:]:
            parameters = list(filter(lambda x: x!='', line.split(";")))

            word = parameters[0]
            freq = np.float128(parameters[-1])
            if not word in frequencies:
                frequencies[word] = freq
            else:
                frequencies[word] += freq

        frequenciesbis = []
        for w in frequencies:
            frequenciesbis.append((w, frequencies[w]))
        frequencies = frequenciesbis[:]
        collator = PyICU.Collator.createInstance(PyICU.Locale('pl_PL.UTF-8'))
        frequencies.sort(key=lambda x: collator.getSortKey(x[0]))

        s = np.float128(0.0)
        self.wordsAbs.append(0.0)
        for d in frequencies:
            self.wordsSpell.append(d[0])
            s += np.float128(d[1])
            self.wordsAbs.append(s)
        self.wordsAbs = np.array(self.wordsAbs)/s
        print(self.wordsAbs)

        file.close()

        #print(self.wordsAbs)
        #self.restart()
        #self.wordsAbs = list(map(lambda x: float(x)/float(s),self.wordsAbs))

    # Used in order to efficiently find which word corresponds to 
    # the current search interval
    def findIndex(self, cursor):
        i = bisect.bisect_right(self.wordsAbs, cursor)
        if i < 0:
            raise ValueError
        return i-1

    # Gives the word corresponding to the current
    # search interval: the closest word to the mid abcisse
    def getWord(self):
        mid = self.curr[-1].mid()
        intervalLength = self.curr[-1].end - self.curr[-1].beg
        randomization = random.uniform(-1, 1) * self.epsilon
        cursor = mid + intervalLength * randomization
        i = self.findIndex(cursor)
        return self.wordsSpell[i]

    # Gives the words corresponding to the interval bound
    def getWordsBound(self):
        i_word_beg = self.findIndex(self.curr[-1].beg)
        i_word_end = self.findIndex(self.curr[-1].end)
        if i_word_end >= len(self.wordsSpell):
            i_word_end = -1
        return self.wordsSpell[i_word_beg],self.wordsSpell[i_word_end]

    # Remove accents from a string
    def removeAccents(self, word):
        return unidecode.unidecode(word)

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
        return i_word_end == i_word_beg


    # Does the left operation
    def left(self):
        mid = self.curr[-1].mid()
        leftIndex = self.findIndex(mid) - 1
        leftAbs = self.wordsAbs[leftIndex]
        self.curr.append(self.curr[-1].left(leftAbs))
        return self.isFinished()

    # Does the right operation
    def right(self):
        mid = self.curr[-1].mid()
        rightIndex = self.findIndex(mid) + 1
        rightAbs = self.wordsAbs[rightIndex]
        self.curr.append(self.curr[-1].right(rightAbs))
        return self.isFinished()

    # Does the discard operation, remove current state
    def discard(self):
        if len(self.curr) > 1:
            self.curr = self.curr[:-1]

    # Test the method on a given word
    # it gives back the number of steps
    def testWord(self, w):
        #print(self.curr)
        #print(self.getWord())
        gets = self.getWord()

        if gets == w:
            return (True,0)

        if self.isFinished():
            return (False,0)

        to_cmp = [gets,w]

        collator = PyICU.Collator.createInstance(PyICU.Locale('pl_PL.UTF-8'))
        to_cmp.sort(key=collator.getSortKey)

        if w == to_cmp[0]:
            self.left()
        else:
            self.right()

        res = self.testWord(w)
        return (res[0],1+res[1])

    # gives back the mean number of trials over the whole dictionary
    # TODO: problem with finding the last word ([:-1] l.167)
    def testAll(self):
        m = 0
        self.restart()
        for w in self.wordsSpell[:-1]:
            print(w)
            res = self.testWord(w)
            self.restart()
            if not res[0]:
                print("Error occurs with word: "+w)
                return
            m += res[1]
        return float(m)/len(self.wordsSpell)

myd = dicotomix()
myd.loadDictionary("LexiqueCompletNormalise.csv")
#myd.testAll()
#exit(1)


# Communication routine
def send(conn, w, prefix):
    print("Sent data: "+w+", "+str(prefix))
    print(myd.getWordsBound())

    #conn.send(bytes(dico[beg]+","+dico[get_mid()]+","+dico[end-1], 'utf-8'))
    word = w.encode('utf-16be')
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
    cmd = conn.recv(BUFFER_SIZE)
    if not cmd: break
    print("received data:", cmd[0])

    if cmd[0] == 1:
        myd.restart()
    if cmd[0] == 2:
        myd.left()
    if cmd[0] == 3:
        myd.right()
    if cmd[0] == 4:
        myd.discard()
    
    send(conn,myd.getWord(),myd.boundPrefix())

conn.close()
