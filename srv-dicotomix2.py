import bisect
import PyICU
import struct 
import socket
import numpy as np
import unidecode

from interval import *

class dicotomix:

    # words_x contains the position that ends
    # a word interval.
    # words_s stores the corresponding word in the
    # same order
    def __init__(self):
        self.curr = interval(0.0,1.0)
        self.s = 0
        self.words_x = []
        self.words_s = []
        #self.init_words2(dict_name,freq)

    def restart(self):
        self.curr = interval(0.0,1.0)

    # Load the dictionary with frequencies when structured
    # as in lexique_complet.csv
    # It's a bit hard coded, sorry for that
    def load_dict(self,dict_name,freq=True):
        f = open(dict_name,"r")
        l = f.read()
        l = list(filter(lambda x: x != '', l.split("\n")))
        dico = {}
        for a in l:
            ll = list(filter(lambda x: x!='',a.split(";")))

            word = ll[1]
            freq = max(map(np.float128,ll[3:-1]))
            if not word in dico:
                dico[word] = freq
            else:
                dico[word] = max(dico[word],freq)

        dicobis = []
        for w in dico:
            dicobis.append((w,dico[w]))
        dico = dicobis[:]
        collator = PyICU.Collator.createInstance(PyICU.Locale('pl_PL.UTF-8'))
        dico.sort(key=lambda x: collator.getSortKey(x[0]))

        if not freq:
            s = 0.0
            delta = float(1/float(len(dico)))
            self.words_x.append(0.0)
            for d in dico:
                self.words_s.append(d[0])
                s += delta
                self.words_x.append(self.s)
        else:
            s = np.float128(0.0)
            self.words_x.append(0.0)
            for d in dico:
                self.words_s.append(d[0])
                s += np.float128(d[1])
                self.words_x.append(s)
            self.words_x = np.array(self.words_x)/s
            print(self.words_x)

        #print(self.words_x)
        #self.restart()
        #self.words_x = list(map(lambda x: float(x)/float(s),self.words_x))

    # Used in order to efficiently find which word corresponds to 
    # the current search interval
    def find_le(self,x):
        i = bisect.bisect_right(self.words_x, x)
        if i:
            return i-1,self.words_x[i-1]
        raise ValueError

    # Gives the word corresponding to the current
    # search interval: the closest word to the mid abcisse
    def get_word(self):
        mid = self.curr.mid()
        i_word = self.find_le(mid)[0]
        return self.words_s[i_word]

    # Gives the words corresponding to the interval bound
    def get_words_bound(self):
        i_word_beg = self.find_le(self.curr.beg)[0]
        i_word_end = self.find_le(self.curr.end)[0]
        if i_word_end >= len(self.words_s):
            i_word_end = -1
        return self.words_s[i_word_beg],self.words_s[i_word_end]

    # Remove accents from a string
    def without_accent(self,w):
        return unidecode.unidecode(w)

    # Give the common prefix of bounds without accent
    def bound_prefix(self):
        w_beg,w_end = self.get_words_bound()
        w_beg = self.without_accent(w_beg)
        w_end = self.without_accent(w_end)
        k = 0
        for i in range(min(len(w_beg),len(w_end))):
            if w_beg[i] != w_end[i]:
                break
            k += 1
        return k

    #If our seeking interval is included
    #in a word interval it's over, we wont find it :(
    def is_finished(self):
        i_word_beg = self.find_le(self.curr.beg)[0]
        i_word_end = self.find_le(self.curr.end)[0]
        return i_word_end == i_word_beg


    # Does the left operation
    def left(self):
        mid = self.curr.mid()
        x_word = self.find_le(mid)[1]
        self.curr = self.curr.left(x_word)
        return self.is_finished()

    # Does the right operation
    def right(self):
        mid = self.curr.mid()
        i_word = self.find_le(mid)[0]
        x_word = self.words_x[i_word+1]
        self.curr = self.curr.right(x_word)
        return self.is_finished()

    # Test the method on a given word
    # it gives back the number of steps
    def find_word(self,w):
        #print(self.curr)
        #print(self.get_word())
        gets = self.get_word()

        if gets == w:
            return (True,0)

        if self.is_finished():
            return (False,0)

        to_cmp = [gets,w]

        collator = PyICU.Collator.createInstance(PyICU.Locale('pl_PL.UTF-8'))
        to_cmp.sort(key=collator.getSortKey)

        if w == to_cmp[0]:
            self.left()
        else:
            self.right()

        res = self.find_word(w)
        return (res[0],1+res[1])

    # It tests the method over the dictionary
    # gives back the mean number of trials
    # TODO: problem with finding the last word ([:-1] l.167)
    def test_yourself(self):
        m = 0
        self.restart()
        for w in self.words_s[:-1]:
            print(w)
            res = self.find_word(w)
            self.restart()
            if not res[0]:
                print("Error occurs with word: "+w)
                return
            m += res[1]
        return float(m)/len(self.words_s)

myd = dicotomix()
myd.load_dict("LexiqueComplet.csv",True)
#myd.test_yourself()
#exit(1)


# Communication routine
def send(conn,w,prefix):
    print("Sent data: "+w+", "+str(prefix))
    print(myd.get_words_bound())

    #conn.send(bytes(dico[beg]+","+dico[get_mid()]+","+dico[end-1], 'utf-8'))
    word = w.encode('utf-16be')
    conn.send(struct.pack(">I", len(word)))
    conn.send(word)
    conn.send(struct.pack(">I", prefix))

#print(myd.find_word("abandonneur"))
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
        send(conn,myd.get_word(),myd.bound_prefix())

    if cmd[0] == 2:
        myd.left()
        send(conn,myd.get_word(),myd.bound_prefix())

    if cmd[0] == 3:
        myd.right()
        send(conn,myd.get_word(),myd.bound_prefix())

conn.close()
