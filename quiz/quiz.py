ifile = open("quiz.dat")

questions = []
responses = []

for line in ifile:
  if "Q: " == line [:3]:
    questions.append ( line[3:-1] )
  elif "R: " == line [:3]:
    responses.append ( line[3:-1] )


## Newbie technique 
counter = 0
for q in questions:
  print (q)
  r_user = input("> ")
  if r_user == responses[counter]:
    print ("Correct!")
  else:
    print ("Non correct: %s" % responses[counter])
  counter += 1


## Intermediate 
for counter, q in enumerate(questions):
  print (q)
  r_user = input("> ")
  r_ok  = responses[counter]
  print ("Correct!" if r_user == r_ok else "Non correct: %s" % r_ok )


## Advanced 
for q, r in zip(questions, responses):
  print (q)
  print ("Correct!" if r==input(">") else "Non correct: %s" % r )  


