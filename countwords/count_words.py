ifile = open("count_words.dat")

words = []
for line in ifile:
  words += list(line[:-1].split())

word_counts = {}
for w in set(words):
  word_counts[w] = words.count(w) 



for nOccurrences in range(10,0,-1):
  w = [k for k, v in word_counts.items() if v==nOccurrences]
  if len(w) == 0:
    continue 
  print ("## Words appearing %d times" % nOccurrences)   
  print ("-----------------------------")   
  print (", ".join(w))
  print ( ) 

