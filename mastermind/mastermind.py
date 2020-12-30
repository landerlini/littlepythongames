import numpy as np 

class MasterMind:
  def __init__ (self, combination):
    self.combination = combination  
    if self.validate(combination) == False:
      raise ValueError ("Invalid combiniation %s" % str(combiniation)) 

  def guess (self, test):
    if self.validate(test) == False: return None, None 
    mp1, mp2 = self.remove_correct (test, self.combination)
    return len(test)-len(mp1), len([c for c in mp1 if c in mp2])

  @staticmethod
  def remove_correct (test, right):
    mp1 = ''.join([x for x,y in zip(test,right) if x != y])
    mp2 = ''.join([y for x,y in zip(test,right) if x != y])
    return mp1, mp2
    

  @staticmethod
  def validate (combination):
    if len(combination) != 4:
      print ("Wrong length")
      return False

    for char in combination:
      if char not in "123456":
        print ("Wrong character %s" % str(char))
        return False


if __name__ == '__main__':
  mmind = MasterMind("%d%d%d%d"%tuple(np.random.randint(1,7,4)))
  for iAttempt in range(8):
    n_ok, n_misplaced = None, None
    while n_ok == None: 
      n_ok, n_misplaced = mmind.guess (input(" %d)> " % (iAttempt+1)))

    if n_ok == len(mmind.combination):
      print ("You win!")
      break 
    else:
      print ("nCorrect: %d   nMisplaced: %d" % (n_ok, n_misplaced))
      exit()

  print ("You lose... :( Solution:", mmind.combination)
