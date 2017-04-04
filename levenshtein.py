#!/usr/bin/python3

def levenshtein(word1, word2):
   word1Length = len(word1)
   word2Length = len(word2)
   if word1Length == 0:
      return word2Length
   elif word2Length == 0:
      return word1Length
   else:
      d = []
      for i in range(word1Length + 1):
         d.append((word2Length + 1) * [0])
         d[i][0] = i


      for j in range(word2Length + 1):
         d[0][j] = j

      for i in range(1,word1Length + 1):
         for j in range(1,word2Length + 1):
            if word1[i - 1] == word2[j - 1]:
               substitutionCost = 0
            else:
               substitutionCost = 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + substitutionCost)

      return d[word1Length][word2Length]
