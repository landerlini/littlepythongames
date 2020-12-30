class MasterMind:
  def __init__ (self, combination):
    self.combination = combination  
    if self.validate(combination) == False:
      raise ValueError ("Invalid combiniation %s" % str(combiniation)) 

  def guess (self, test):
    if self.validate(test) == False: return None, None 
    wrong_only = self.remove_correct (test, self.combination)
    print (wrong_only)
    return len(test)-len(wrong_only), len([c for c in test if c in wrong_only])

  @staticmethod
  def remove_correct (test, right):
    return ''.join([y for x,y in zip(test,right) if x != y])
    

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
  mmind = MasterMind("1234")
  for iAttempt in range(8):
    n_ok, n_misplaced = None, None
    while n_ok == None: 
      n_ok, n_misplaced = mmind.guess (input(" %d)> " % (iAttempt+1)))

    if n_ok == len(mmind.combination):
      print ("You win!")
      break 
    else:
      print ("nCorrect: %d   nMisplaced: %d" % (n_ok, n_misplaced))

  print ("You lose... :(")
